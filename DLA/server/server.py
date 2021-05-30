from __future__ import annotations

import asyncio
import os
import pkgutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, Optional, cast
from uuid import uuid4

import numpy as np
import yaml


@dataclass
class WorkData:
    beta: float
    start_time: float = field(default_factory=time.time, init=False)


is_done = False
check_old_works_lock: asyncio.Lock
works: Dict[int, WorkData] = {}
memory_counter = {
    -0.99 + (i * 0.01): 100 for i in range(199)
}
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

    async def get(self) -> Optional[float]:
        async with self.lock:
            t = tuple(k for k, v in self.to_distribute.items() if v)
            if not (t or any(self.waiting_for_results.values())):
                return None
            val = np.random.choice(t)
            self.to_distribute[val] -= 1
            self.waiting_for_results[val] += 1
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
        beta = await work_gen.get()

        if beta is None:
            writer.close()
            return

        work_uuid = uuid4()
        work_id_int = work_uuid.int
        work_id_bytes = work_uuid.bytes

        config = CONFIG_TEMPLATE.copy()
        config['memory'] = beta

        writer.write(work_id_bytes)

        writer.write(cast(str, yaml.dump(config)).encode('utf-8'))
        await writer.drain()

        try:
            await asyncio.wait_for(reader.read(1), 60 * 10)
        except asyncio.TimeoutError:
            await work_gen.work_timeouted(beta)
        else:
            await work_gen.work_completed(beta)
            name_len = int(await reader.read(1))
            file_name = (await reader.read(name_len)).decode('utf-8')
            data = await reader.read(-1)

            (out_dir / str(beta) / file_name).write_bytes(data)

        writer.close()

    return _handle_request


# src: https://docs.python.org/3/library/asyncio-stream.html
async def serve(out_dir: Path):
    serv = await asyncio.start_server(
        handle_request(out_dir),
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    print(f"Serving at: {addr}")

    async with serv:
        await serv.serve_forever()


async def check_old_works():
    # wait first 10 minutes, to let first works run
    limit = 60 * 10
    await asyncio.sleep(limit)
    while not is_done:
        async with check_old_works_lock:
            t = time.time()
            for k, v in works.copy().items():
                if t - v.start_time > limit:
                    works.pop(k)
                    work_gen.work_timeouted(k)

        await asyncio.sleep(60 * 2)  # check every 2 minutes


async def server(out_dir: Path) -> None:
    global check_old_works_lock
    global work_gen
    check_old_works_lock = asyncio.Lock()
    work_gen = WorkGenerator(-0.99, 0.99, 0.1, 10)
    t1 = asyncio.create_task(serve(out_dir))
    t2 = asyncio.create_task(check_old_works())
    await t1
    await t2


asyncio.run(server(Path('.')))