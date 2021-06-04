from __future__ import annotations

import asyncio
import os
from pathlib import Path
from socket import socket
from typing import Any, Callable, Coroutine, cast
from uuid import uuid4

import yaml
from loguru import logger

from DLA.server.connections import Connections
from DLA.server.work_generator import WorkGenerator

from .config import CONFIG_TEMPLATE, END, NUM_OF_SAMPLES, START, STEP

logger.add('server_{time}.log', format='{time} | {level} | {message}')


def handle_request(
    out_dir: Path,
    conn: Connections,
    work_gen: WorkGenerator
) -> Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Coroutine[Any, Any, None]
]:
    async def _handle_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        sock: socket = writer.transport._sock  # type: ignore
        client_ip = sock.getpeername()[0]
        if conn.is_closed():
            writer.write(b'\01')
            logger.info(
                f'Server is closing, reject connection from: {client_ip}'
            )
            return

        await conn.connect()

        work_id = uuid4().hex

        logger.info(
            f'{work_id} - Client connected, connection from {client_ip}')

        beta = await work_gen.get()

        if beta is None:
            writer.write(b'\01')
            await writer.drain()
            writer.close()
            logger.info(f'{work_id} - No work to assign.')
            await conn.disconnect()
            return

        writer.write(b'\00')
        await writer.drain()

        config = CONFIG_TEMPLATE.copy()
        config['memory'] = beta

        writer.write(work_id.encode('utf-8'))

        _config = cast(str, yaml.dump(config)).encode('utf-8')
        writer.write(len(_config).to_bytes(4, 'big'))
        writer.write(_config)
        await writer.drain()

        logger.info(f'{work_id} - Assigned work, {beta=}')

        try:
            logger.info(f'{work_id} - Waiting for work to complete.')
            await asyncio.wait_for(reader.read(1), 60 * 10)
        except asyncio.TimeoutError:
            writer.write(b'\01')
            logger.warning(f'{work_id} - Work timed out.')
            await work_gen.work_timeouted(beta)
        else:
            try:
                writer.write(b'\00')
                name_len = int.from_bytes(await reader.read(1), 'big')
                file_name = (await reader.read(name_len)).decode('utf-8')
                data = await reader.read(-1)

                out_file = out_dir / file_name
                out_file.parent.mkdir(exist_ok=True, parents=True)

                out_file.write_bytes(data)

                logger.info(
                    f'{work_id} - Work completed, saved to file {out_file}'
                )
                await work_gen.work_completed(beta)
            except Exception as e:
                logger.error(f'{work_id} - Exception: {e}')
                try:
                    if out_file.exists():
                        out_file.unlink()
                except Exception:
                    pass
                finally:
                    await work_gen.work_timeouted(beta)
                    await conn.disconnect()

        writer.close()
        await writer.wait_closed()

        await conn.disconnect()

        if not (conn.is_closed() or await work_gen.are_values_left()):
            logger.info(
                f'{work_id} - There are no more values to assign. '
                'Starting to close the server.'
            )
            conn.close()

    return _handle_request


# src: https://docs.python.org/3/library/asyncio-stream.html
@logger.catch
async def server(out_dir: Path) -> None:
    work_gen = WorkGenerator(START, END, STEP, NUM_OF_SAMPLES)
    close_server = asyncio.Event()

    conn = Connections(close_server)

    serv = await asyncio.start_server(
        handle_request(out_dir, conn, work_gen),
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
