from __future__ import annotations

import asyncio


class ConnectionTracker:
    def __init__(self, event: asyncio.Event) -> None:
        self.lock = asyncio.Lock()
        self.connections = 0
        self.end_event = event

    async def connect(self) -> None:
        async with self.lock:
            self.connections += 1

    async def disconnect(self) -> None:
        async with self.lock:
            self.connections -= 1

    async def are_connections_left(self) -> bool:
        async with self.lock:
            return bool(self.connections)

    def close(self) -> None:
        self.end_event.set()

    def is_closed(self) -> bool:
        return self.end_event.is_set()
