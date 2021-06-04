from __future__ import annotations

import asyncio
import os
from pathlib import Path

from loguru import logger

from DLA.server.connections import Connections
from DLA.server.server_handler import Handler
from DLA.server.work_generator import WorkGenerator

from .config import END, NUM_OF_SAMPLES, START, STEP

logger.add('server_{time}.log', format='{time} | {level} | {message}')


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
