from __future__ import annotations

import asyncio
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Final

from loguru import logger

logger.add('client_{time}.log', format='{time} | {level} | {message}')


SERVER_ADDR: Final[str] = os.environ.get('DLA_SERVER', 'localhost')
SERVER_PORT: Final[int] = int(os.environ.get('DLA_PORT', 1025))
EXEC: Final[str] = sys.executable


async def execute_work(config: str) -> str:
    proc = await asyncio.create_subprocess_exec(
        EXEC, "-m", "DLA", "simulate", "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )
    return (
        await proc.communicate(config.encode('utf-8'))
    )[0].decode('utf-8').strip()


@logger.catch
async def run_work() -> bool:
    tmp_work_id = uuid.uuid4().hex
    logger.info(f'Temporary work_id = {tmp_work_id}')

    reader, writer = await asyncio.open_connection(SERVER_ADDR, SERVER_PORT)

    logger.info(f'{tmp_work_id} - Connected to server.')

    if await reader.read(1) == b'\01':
        logger.warning(f'{tmp_work_id} - No work to do.')
        writer.close()
        await writer.wait_closed()
        return True

    work_id = (await reader.read(32)).decode('utf-8')
    logger.info(f'Temporary work id ({tmp_work_id}) replaced with {work_id}.')

    config_len = int.from_bytes(await reader.read(4), 'big')
    config: str = (await reader.read(config_len)).decode('utf-8')

    logger.info(f'{work_id} - Started executing work.')

    start_time = time.time()

    out_file = await execute_work(config)

    delta_time = (time.time() - start_time) / 60

    try:
        writer.write(b'\01')
        await writer.drain()

        if await reader.read(1) == b'\01':
            logger.warning(f'{work_id} - Timeout.')
            writer.close()
            return False

        writer.write(len(out_file).to_bytes(1, 'big'))
        writer.write(out_file.encode('utf-8'))

        writer.write(Path(out_file).absolute().read_bytes())
        await writer.drain()

        logger.info(
            f'{work_id} - Work finished, took {delta_time}s, results send.'
        )
    except ConnectionError as e:
        logger.warning(f'{work_id} - {e}')
        writer.close()
        return True
    else:
        writer.close()
        await writer.wait_closed()
        logger.info(f'{work_id} - Closed connection.')

    return False


async def run_clients(num_of_clients: int) -> None:
    while not any(
        await asyncio.gather(*[run_work() for _ in range(num_of_clients)])
    ):
        pass


if __name__ == '__main__':
    asyncio.run(run_work())
