from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import os
from pathlib import Path
import time
from typing import Any, Callable, Coroutine, Dict


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


async def send_work_to_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    print("Send")


async def receive_data_from_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    print("Receive")


CONNECTION_TYPE: Dict[
    bytes, Callable[
        [asyncio.StreamReader, asyncio.StreamWriter],
        Coroutine[Any, Any, None]
    ]
] = {
    b'\x00': send_work_to_client,
    b'\x01': receive_data_from_client,

}


async def handle_request(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    conn_type = await reader.read(1)
    try:
        await CONNECTION_TYPE[conn_type](reader, writer)
    except KeyError:
        pass
    finally:
        writer.close()


# src: https://docs.python.org/3/library/asyncio-stream.html
async def serve():
    serv = await asyncio.start_server(
        handle_request,
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
                    memory_counter[v.beta] += 1

        await asyncio.sleep(60 * 2)  # check every 2 minutes


async def server(out_dir: Path) -> None:
    t1 = asyncio.create_task(serve())
    t2 = asyncio.create_task(check_old_works())
    await t1
    await t2


asyncio.run(server(Path('.')))
