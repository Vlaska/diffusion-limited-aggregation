from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from functools import partialmethod
from typing import Optional, Union
from uuid import uuid4

from loguru import logger

from DLA.server import FAIL, SUCCESS


@dataclass
class ConnData:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    work_id: str = field(default_factory=lambda: uuid4().hex, init=False)
    beta: Optional[float] = field(init=False)

    async def send_id_to_client(self) -> None:
        await self.write(self.work_id)

    def log(self, msg: str, level: str) -> None:
        getattr(logger, level)(f'{self.work_id} - {msg}')

    async def write(self, msg: Union[bytes, str]) -> None:
        if isinstance(msg, str):
            msg = msg.encode('utf-8')

        self.writer.write(msg)
        await self.writer.drain()

    async def read(self, size: int) -> bytes:
        return await self.reader.read(size)

    async def close(self) -> None:
        self.writer.close()
        try:
            await asyncio.wait_for(self.writer.wait_closed(), 60)
        except Exception:
            self.warning('Trouble with closing connection.')

    info = partialmethod(log, level='info')
    warning = partialmethod(log, level='warning')
    error = partialmethod(log, level='error')

    failed = partialmethod(write, msg=FAIL)
    success = partialmethod(write, msg=SUCCESS)
