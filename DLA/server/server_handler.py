from __future__ import annotations

import asyncio
from pathlib import Path
from socket import socket
from typing import cast

import yaml

from DLA.server.config import CONFIG_TEMPLATE, TIMEOUT
from DLA.server.connection_data import ConnData
from DLA.server.connections import Connections
from DLA.server.work_generator import WorkGenerator


class Disconnected(Exception):
    pass


class Handler:
    def __init__(
        self, out_dir: Path, conn: Connections, work_gen: WorkGenerator
    ) -> None:
        self.out_dir = out_dir
        self.conn = conn
        self.work_gen = work_gen
        self.out_dir.mkdir(parents=True, exist_ok=True)

    async def gen_beta(self, conn_data: ConnData):
        beta = await self.work_gen.get()
        conn_data.beta = beta

    async def send_config(self, conn_data: ConnData) -> None:
        config = CONFIG_TEMPLATE.copy()
        config['simulation']['memory'] = conn_data.beta

        config_dump = cast(str, yaml.dump(config)).encode('utf-8')
        await conn_data.write(
            len(config_dump).to_bytes(4, 'big') + config_dump
        )

    async def save_results(self, conn_data: ConnData) -> bool:
        try:
            name_len = int.from_bytes(await conn_data.read(1), 'big')
            filename = (await conn_data.read(name_len)).decode('utf-8')
            data = await conn_data.read(-1)

            out_file = self.out_dir / filename
            out_file.write_bytes(data)
            conn_data.info(f'Work completed, saved to "{out_file}"')

            await self.work_gen.work_completed(cast(float, conn_data.beta))

            return True
        except PermissionError:
            conn_data.warning('Disconnected.')
        except Exception as e:
            conn_data.error(f'Exception: {e}')

        try:
            if out_file.exists():
                out_file.unlink()
        except Exception:
            pass

        return False

    async def _handle_request(self, conn_data: ConnData) -> None:
        sock: socket = conn_data.writer.transport._sock  # type: ignore
        client_ip = sock.getpeername()[0]

        conn_data.info(
            f'Client connected, connection from {client_ip}'
        )

        if self.conn.is_closed():
            await conn_data.failed()
            conn_data.info(
                f'Server is closing, reject connection from: {client_ip}'
            )
            await conn_data.close()
            return

        await self.conn.connect()
        await self.gen_beta(conn_data)

        if conn_data.beta is None:
            await conn_data.failed()
            conn_data.info('No work to assign.')

            await conn_data.close()
            await self.conn.disconnect()
            return

        await conn_data.success()
        await conn_data.send_id_to_client()
        await self.send_config(conn_data)

        conn_data.info(
            f'Assigned work, beta = {conn_data.beta}. '
            'Waiting for work to finnish.'
        )

        try:
            result = await asyncio.wait_for(conn_data.read(1), TIMEOUT)
            if result == b'':
                raise Disconnected()
        except asyncio.TimeoutError:
            await conn_data.failed()
            conn_data.warning('Work timed out.')
            await self.work_gen.work_timeouted(conn_data.beta)
        except Disconnected:
            conn_data.warning('Client got disconnected.')
            await self.work_gen.work_timeouted(conn_data.beta)
        else:
            await conn_data.success()
            if not await self.save_results(conn_data):
                await self.work_gen.work_timeouted(conn_data.beta)

        await conn_data.close()
        await self.conn.disconnect()

    async def handle_request(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        conn_data = ConnData(reader, writer)
        await self._handle_request(conn_data)
        if not (
            self.conn.is_closed() or await self.work_gen.are_values_left(False)
        ):
            conn_data.info(
                'There are no more work to assign. '
                'Starting to close the server'
            )
            self.conn.close()
