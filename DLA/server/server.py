from __future__ import annotations

import asyncio
import os
import pkgutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, Optional, cast

import numpy as np
import yaml


@dataclass
class WorkData:
    beta: float
    start_time: float = field(default_factory=time.time, init=False)


is_done = False
check_old_works_lock = asyncio.Lock()
works: Dict[int, WorkData] = {}
memory_counter = {
    -0.99 + (i * 0.01): 100 for i in range(199)
}
CONFIG_TEMPLATE: Dict[str, Any] = yaml.full_load(
    cast(bytes, pkgutil.get_data('DLA.server', 'config_template.yml'))
)


class WorkGenerator:
    lock = asyncio.Lock()

    def __init__(self, start: float, end: float, step: float, num: int):
        _points = end - start
        points = int(_points)
        while _points != points:
            _points *= 10
            points = int(_points)
        self.to_distribute = {
            -start + (i * step): num for i in range(points + 1)
        }
        self.waiting_for_results = {
            -start + (i * step): 0 for i in range(points + 1)
        }

    async def get(self) -> Optional[float]:
        async with self.lock:
            t = (k for k, v in self.to_distribute.items() if v)
            if not (t or any(self.waiting_for_results.values())):
                return None
            val = np.random.choice(t)
            self.to_distribute[val] -= 1
            self.waiting_for_results[val] += 1
        return val

    async def work_completed(self, val: float) -> None:
        async with self.lock:
            self.waiting_for_results[val] -= 1

    async def work_timeouted(self, val: float) -> None:
        async with self.lock:
            self.to_distribute[val] += 1
            self.waiting_for_results[val] -= 1


work_gen = WorkGenerator(-0.99, 0.99, 0.1, 10)


async def send_work_to_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    out_dir: Path
) -> None:
    print("Send")


async def receive_data_from_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    out_dir: Path
) -> None:
    print("Receive")


CONNECTION_TYPE: Dict[
    bytes, Callable[
        [asyncio.StreamReader, asyncio.StreamWriter, Path],
        Coroutine[Any, Any, None]
    ]
] = {
    b'\x00': send_work_to_client,
    b'\x01': receive_data_from_client,
}


def handle_request(out_dir: Path) -> Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Coroutine[Any, Any, None]
]:
    async def _handle_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        conn_type = await reader.read(1)
        try:
            async with check_old_works_lock:
                await CONNECTION_TYPE[conn_type](reader, writer, out_dir)
        except KeyError:
            pass
        finally:
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
    t1 = asyncio.create_task(serve(out_dir))
    t2 = asyncio.create_task(check_old_works())
    await t1
    await t2


asyncio.run(server(Path('.')))
