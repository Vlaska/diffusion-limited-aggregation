from __future__ import annotations
from DLA.server.worker import Worker

import asyncio
import os
from pathlib import Path
from typing import Final

from loguru import logger

logger.add('client_{time}.log', format='{time} | {level} | {message}')


SERVER_ADDR: Final[str] = os.environ.get('DLA_SERVER', 'localhost')
SERVER_PORT: Final[int] = int(os.environ.get('DLA_PORT', 1025))


@logger.catch
async def run_work() -> bool:
    reader, writer = await asyncio.open_connection(SERVER_ADDR, SERVER_PORT)

    logger.info('Connected to server.')

    if await reader.read(1) == b'\01':
        logger.warning('No work.')
        writer.close()
        await writer.wait_closed()
        return True

    work_id = int.from_bytes(await reader.read(16), 'big')
    logger.info(f'{work_id=}')

    config_len = int.from_bytes(await reader.read(4), 'big')
    config: str = (await reader.read(config_len)).decode('utf-8')

    worker = Worker(work_id, config)
    logger.info(f'{work_id} - Started executing work.')
    out_file = await worker.execute_work()
    logger.info(f'{work_id} - Work finished.')
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

        logger.info(f'{work_id} - Send results.')
    except ConnectionError as e:
        logger.warning(f'{work_id} - {e}')

    writer.close()
    await writer.wait_closed()
    logger.info(f'{work_id} - Closed connection.')

    return False

if __name__ == '__main__':
    asyncio.run(run_work())
