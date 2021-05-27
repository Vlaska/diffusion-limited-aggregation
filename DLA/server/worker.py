from __future__ import annotations

import asyncio
from pathlib import Path
import pickle
import sys


class Worker:
    def __init__(self, work_id: int, config: str) -> None:
        self.work_id = work_id
        self.config = config

    async def execute_work(self) -> str:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "DLA", "simulate", "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        return (
            await proc.communicate(self.config.encode('utf-8'))
        )[0].decode('utf-8').strip()

    async def return_results_to_server(
        self,
        writer: asyncio.StreamWriter,
        data_path: str
    ) -> None:
        data = pickle.dumps((
            self.work_id,
            Path(data_path).read_bytes()
        ))
        writer.write(data)
        await writer.drain()

    @staticmethod
    async def send_config_to_client(
        writer: asyncio.StreamWriter,
        work_id: int, config: str
    ) -> None:
        data = pickle.dumps((work_id, config))
        writer.write(data)
        await writer.drain()

    @staticmethod
    async def load_workder_from_server(reader: asyncio.StreamReader) -> Worker:
        d = pickle.loads(await reader.read(-1))
        return Worker(*d)
