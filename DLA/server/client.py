from __future__ import annotations

import asyncio
import os
import sys
import time
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Final

from loguru import logger

from DLA.server import FAIL, SUCCESS

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

    try:
        reader, writer = await asyncio.open_connection(
            SERVER_ADDR, SERVER_PORT
        )
    except ConnectionRefusedError:
        logger.warning(
            f'{tmp_work_id} - Connection to server refused. Closing clients.'
        )
        return True

    logger.info(f'{tmp_work_id} - Connected to server.')

    if await reader.read(1) == FAIL:
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
    out_file_encoded = out_file.encode('utf-8')

    delta_time = time.time() - start_time

    try:
        writer.write(SUCCESS)
        await writer.drain()

        if await asyncio.wait_for(reader.read(1), 3 * 60) == FAIL:
            logger.warning(f'{work_id} - Timeout.')
            writer.close()
            return False

        writer.write(len(out_file_encoded).to_bytes(1, 'big'))
        writer.write(out_file_encoded)

        writer.write(Path(out_file).absolute().read_bytes())
        await writer.drain()

        logger.info(
            f'{work_id} - Work finished, took {timedelta(seconds=delta_time)},'
            ' results send.'
        )
    except (ConnectionError, asyncio.TimeoutError) as e:
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
