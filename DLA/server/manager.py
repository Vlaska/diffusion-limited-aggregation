from __future__ import annotations

import asyncio
import pickle


class Manager:
    def __init__(self, work_id: int, config: str) -> None:
        self.work_id = work_id
        self.config = config

    async def send_to_worker(self, writer: asyncio.StreamWriter) -> None:
        writer.write(pickle.dumps(self))
        await writer.drain()

    async def start_work(self) -> None:
        pass
