from __future__ import annotations

import asyncio
import os
import pkgutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, cast
from uuid import uuid4

from loguru import logger
import numpy as np
import yaml


logger.add('server_{time}.log', format='{time} | {level} | {message}')


@dataclass
class WorkData:
    beta: float
    start_time: float = field(default_factory=time.time, init=False)


is_done = False
CONFIG_TEMPLATE: Dict[str, Any] = yaml.full_load(
    cast(bytes, pkgutil.get_data('DLA.server', 'config_template.yml'))
)


class WorkGenerator:
    lock: asyncio.Lock

    def __init__(self, start: float, end: float, step: float, num: int):
        self.__class__.lock = asyncio.Lock()
        _points = end - start
        points = int(_points)
        while _points != points:
            _points *= 10
            points = int(_points)
        tmp = np.arange(start, end, step)
        self.to_distribute = {
            i: num for i in tmp
        }
        self.waiting_for_results = {
            i: 0 for i in tmp
        }

    def _gather_beta_values(self) -> Tuple[float, ...]:
        return tuple(k for k, v in self.to_distribute.items() if v)

    async def are_values_left(self, is_locked: bool = True) -> bool:
        if not is_locked:
            await self.lock.acquire()

        val = bool(
            self._gather_beta_values() or
            tuple(
                k
                for k, v in self.waiting_for_results.items()
                if v
            ))

        if not is_locked:
            self.lock.release()

        return val

    async def _is_done(self) -> bool:
        await self.lock.acquire()
        if self._gather_beta_values():
            return False

        if any(self.waiting_for_results.values()):
            while await self.are_values_left(True):
                self.lock.release()
                await asyncio.sleep(30)
                await self.lock.acquire()
            return False

        self.lock.release()
        return True

    async def get(self) -> Optional[float]:
        if await self._is_done():
            return None

        t = self._gather_beta_values()

        val = np.random.choice(t)
        self.to_distribute[val] -= 1
        self.waiting_for_results[val] += 1

        self.lock.release()

        return float(val)

    async def work_completed(self, val: float) -> None:
        async with self.lock:
            self.waiting_for_results[val] -= 1

    async def work_timeouted(self, val: float) -> None:
        async with self.lock:
            self.to_distribute[val] += 1
            self.waiting_for_results[val] -= 1


work_gen: WorkGenerator


def handle_request(out_dir: Path) -> Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Coroutine[Any, Any, None]
]:
    async def _handle_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        work_uuid = uuid4()
        work_id_int = work_uuid.int
        work_id_bytes = work_uuid.bytes

        logger.info(f'{work_id_int} - Client connected')

        logger.bind(work_id=work_id_int)

        beta = await work_gen.get()

        if beta is None:
            writer.close()
            logger.info(f'{work_id_int} - No work to assign.')
            return

        config = CONFIG_TEMPLATE.copy()
        config['memory'] = beta

        writer.write(work_id_bytes)

        writer.write(cast(str, yaml.dump(config)).encode('utf-8'))
        await writer.drain()

        logger.info(f'{work_id_int} - Assigned work, {beta=}')

        try:
            await asyncio.wait_for(reader.read(1), 60 * 10)
        except asyncio.TimeoutError:
            logger.warning(f'{work_id_int} - Work timed out.')
            await work_gen.work_timeouted(beta)
        else:
            await work_gen.work_completed(beta)
            name_len = int(await reader.read(1))
            file_name = (await reader.read(name_len)).decode('utf-8')
            data = await reader.read(-1)

            out_file = out_dir / str(beta) / file_name

            out_file.write_bytes(data)

            logger.info(
                f'{work_id_int} - Work completed, saved to file {out_file}'
            )

        writer.close()

    return _handle_request


# src: https://docs.python.org/3/library/asyncio-stream.html
async def server(out_dir: Path) -> None:
    global work_gen
    work_gen = WorkGenerator(-0.99, 0.99, 0.1, 10)

    serv = await asyncio.start_server(
        handle_request(out_dir),
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    logger.info(f"Serving at: {addr}")

    async with serv:
        await serv.serve_forever()


asyncio.run(server(Path('.')))
