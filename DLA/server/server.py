from __future__ import annotations

import asyncio
import os
import pkgutil
from pathlib import Path
from socket import socket
from typing import Any, Callable, Coroutine, Dict, Optional, Tuple, cast
from uuid import uuid4

from loguru import logger
import numpy as np
import yaml


logger.add('server_{time}.log', format='{time} | {level} | {message}')


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


work_gen: WorkGenerator
close_server: asyncio.Event


def handle_request(out_dir: Path) -> Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Coroutine[Any, Any, None]
]:
    async def _handle_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        work_uuid = uuid4()
        work_id_int = work_uuid.int
        work_id_bytes = work_uuid.bytes
        sock: socket = writer.transport._sock  # type: ignore

        logger.info(
            f'{work_id_int} - Client connected, connection from ' +
            sock.getpeername()[0]
        )

        logger.bind(work_id=work_id_int)

        beta = await work_gen.get()

        if beta is None:
            writer.write(b'\01')
            await writer.drain()
            writer.close()
            logger.info(f'{work_id_int} - No work to assign.')
            return

        writer.write(b'\00')
        await writer.drain()

        config = CONFIG_TEMPLATE.copy()
        config['memory'] = beta

        writer.write(work_id_bytes)

        _config = cast(str, yaml.dump(config)).encode('utf-8')
        writer.write(len(_config).to_bytes(4, 'big'))
        writer.write(_config)
        await writer.drain()

        logger.info(f'{work_id_int} - Assigned work, {beta=}')

        try:
            logger.info(f'{work_id_int} - Waiting for work to complete.')
            await asyncio.wait_for(reader.read(1), 10)
        except asyncio.TimeoutError:
            writer.write(b'\01')
            logger.warning(f'{work_id_int} - Work timed out.')
            await work_gen.work_timeouted(beta)
        else:
            writer.write(b'\00')
            await work_gen.work_completed(beta)
            name_len = int.from_bytes(await reader.read(1), 'big')
            file_name = (await reader.read(name_len)).decode('utf-8')
            data = await reader.read(-1)

            out_file = out_dir / file_name
            out_file.parent.mkdir(exist_ok=True, parents=True)

            out_file.write_bytes(data)

            logger.info(
                f'{work_id_int} - Work completed, saved to file {out_file}'
            )

        writer.close()
        await writer.wait_closed()

    return _handle_request


# src: https://docs.python.org/3/library/asyncio-stream.html
@logger.catch
async def server(out_dir: Path) -> None:
    global work_gen
    work_gen = WorkGenerator(-0.99, 0.99, 0.99, 1)

    serv = await asyncio.start_server(
        handle_request(out_dir),
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    logger.info(f"Serving at: {addr}")

    async with serv:
        await serv.serve_forever()


asyncio.run(server(Path('./out')), debug=True)
