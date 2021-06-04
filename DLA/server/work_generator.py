from __future__ import annotations

import asyncio
from typing import Optional, Tuple

import numpy as np


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

        if bool(self.waiting_for_results.values()):
            while await self.are_values_left(True):
                if bool(self._gather_beta_values()):
                    return False

                self.lock.release()
                await asyncio.sleep(5)
                await self.lock.acquire()

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
