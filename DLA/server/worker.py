from __future__ import annotations

import asyncio
import sys
import pickle


class Worker:
    def __init__(self, work_id: int, config: str) -> None:
        self.work_id = work_id
        self.config = config

    async def send_to_worker(self, writer: asyncio.StreamWriter) -> None:
        writer.write(pickle.dumps(self))
        await writer.drain()

    async def _run_work(self) -> str:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "DLA", "simulate", "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        return (
            await proc.communicate(self.config.encode('utf-8'))
        )[0].decode('utf-8').strip()

    async def start_work(self) -> bool:
        pass

    async def return_results(self, writer: asyncio.StreamWriter) -> None:
        pass
