from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from functools import partialmethod
from pathlib import Path
from socket import socket
from typing import Optional, Union, cast
from uuid import uuid4

import yaml
from loguru import logger

from DLA.server import FAIL, SUCCESS
from DLA.server.connections import Connections
from DLA.server.work_generator import WorkGenerator

from .config import CONFIG_TEMPLATE, END, NUM_OF_SAMPLES, START, STEP, TIMEOUT

logger.add('server_{time}.log', format='{time} | {level} | {message}')


@dataclass
class WorkData:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    work_id: str = field(default_factory=lambda: uuid4().hex, init=False)
    beta: Optional[float] = field(init=False)

    async def send_id_to_client(self) -> None:
        await self.write(self.work_id)

    def log(self, msg: str, level: str) -> None:
        getattr(logger, level)(f'{self.work_id} - {msg}')

    async def write(self, msg: Union[bytes, str]) -> None:
        if isinstance(msg, str):
            msg = msg.encode('utf-8')

        self.writer.write(msg)
        await self.writer.drain()

    async def read(self, size: int) -> bytes:
        return await self.reader.read(size)

    async def close(self) -> None:
        self.writer.close()
        try:
            await asyncio.wait_for(self.writer.wait_closed(), 60)
        except Exception:
            self.warning('Trouble with closing connection.')

    info = partialmethod(log, level='info')
    warning = partialmethod(log, level='warning')
    error = partialmethod(log, level='error')

    failed = partialmethod(write, msg=FAIL)
    success = partialmethod(write, msg=SUCCESS)


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

    async def gen_beta(self, work_data: WorkData):
        beta = await self.work_gen.get()
        work_data.beta = beta

    async def send_config(self, work_data: WorkData) -> None:
        config = CONFIG_TEMPLATE.copy()
        config['beta'] = work_data.beta

        config_dump = cast(str, yaml.dump(config)).encode('utf-8')
        await work_data.write(
            len(config_dump).to_bytes(4, 'big') + config_dump
        )

    async def save_results(self, work_data: WorkData) -> bool:
        try:
            name_len = int.from_bytes(await work_data.read(1), 'big')
            filename = (await work_data.read(name_len)).decode('utf-8')
            data = await work_data.read(-1)

            out_file = self.out_dir / filename
            out_file.write_bytes(data)
            work_data.info(f'Work completed, saved to "{out_file}"')

            await self.work_gen.work_completed(cast(float, work_data.beta))

            return True
        except PermissionError:
            work_data.warning('Disconnected.')
        except Exception as e:
            work_data.error(f'Exception: {e}')

        try:
            if out_file.exists():
                out_file.unlink()
        except Exception:
            pass

        return False

    async def _handle_request(self, work_data: WorkData) -> None:
        sock: socket = work_data.writer.transport._sock  # type: ignore
        client_ip = sock.getpeername()[0]

        work_data.info(
            f'Client connected, connection from {client_ip}'
        )

        if self.conn.is_closed():
            await work_data.failed()
            work_data.info(
                f'Server is closing, reject connection from: {client_ip}'
            )
            await work_data.close()
            return

        await self.conn.connect()
        await self.gen_beta(work_data)

        if work_data.beta is None:
            await work_data.failed()
            work_data.info(f'No work to assign.')

            await work_data.close()
            await self.conn.disconnect()
            return

        await work_data.success()
        await work_data.send_id_to_client()
        await self.send_config(work_data)

        work_data.info(
            f'Assigned work, beta = {work_data.beta}. '
            'Waiting for work to finnish.'
        )

        try:
            result = await asyncio.wait_for(work_data.read(1), TIMEOUT)
            if result == b'':
                raise Disconnected()
        except asyncio.TimeoutError:
            await work_data.failed()
            work_data.warning('Work timed out.')
            await self.work_gen.work_timeouted(work_data.beta)
        except Disconnected:
            work_data.warning('Client got disconnected.')
            await self.work_gen.work_timeouted(work_data.beta)
        else:
            await work_data.success()
            if not await self.save_results(work_data):
                await self.work_gen.work_timeouted(work_data.beta)

        await work_data.close()
        await self.conn.disconnect()

    async def handle_request(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        work_data = WorkData(reader, writer)
        await self._handle_request(work_data)
        if not (
            self.conn.is_closed() or await self.work_gen.are_values_left(False)
        ):
            work_data.info(
                'There are no more work to assign. '
                'Starting to close the server'
            )
            self.conn.close()


# src: https://docs.python.org/3/library/asyncio-stream.html
@logger.catch
async def server(out_dir: Path) -> None:
    work_gen = WorkGenerator(START, END, STEP, NUM_OF_SAMPLES)
    close_server = asyncio.Event()
    conn = Connections(close_server)

    handler = Handler(out_dir, conn, work_gen)

    serv = await asyncio.start_server(
        handler.handle_request,
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    logger.info(f"Serving at: {addr}")

    await close_server.wait()

    while True:
        if not await conn.are_connections_left():
            break
        logger.info('Waiting for all connections to end.')
        await asyncio.sleep(10)

    serv.close()
    await serv.wait_closed()
    logger.info('Server closed.')


if __name__ == '__main__':
    asyncio.run(server(Path('./out')), debug=True)
