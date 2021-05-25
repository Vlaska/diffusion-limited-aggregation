from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict


async def send_work_to_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    pass


async def receive_data_from_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    pass


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
    CONNECTION_TYPE[conn_type](reader, writer)


# src: https://docs.python.org/3/library/asyncio-stream.html
async def server(out_dir: Path) -> None:
    serv = await asyncio.start_server(
        handle_request,
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    print(f"Serving at: {addr}")

    async with serv:
        await serv.serve_forever()
