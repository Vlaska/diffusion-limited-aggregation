from __future__ import annotations

import asyncio
import os
from pathlib import Path
from socket import socket
from typing import Any, Callable, Coroutine, Optional, Tuple, cast
from uuid import uuid4

import numpy as np
import yaml
from loguru import logger

from .config import CONFIG_TEMPLATE, END, NUM_OF_SAMPLES, START, STEP

logger.add('server_{time}.log', format='{time} | {level} | {message}')


class Connections:
    def __init__(self, event: asyncio.Event) -> None:
        self.lock = asyncio.Lock()
        self.connections = 0
        self.end_event = event

    async def connect(self) -> None:
        with self.lock:
            self.connections += 1

    async def disconnect(self) -> None:
        with self.lock:
            self.connections -= 1

    async def are_connections_left(self) -> bool:
        with self.lock:
            return bool(self.connections)

    def close(self) -> None:
        self.end_event.set()

    def is_closed(self) -> bool:
        return self.end_event.is_set()


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


def handle_request(
    out_dir: Path,
    conn: Connections,
    work_gen: WorkGenerator
) -> Callable[
    [asyncio.StreamReader, asyncio.StreamWriter],
    Coroutine[Any, Any, None]
]:
    async def _handle_request(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        sock: socket = writer.transport._sock  # type: ignore
        client_ip = sock.getpeername()[0]
        if conn.is_closed():
            writer.write(b'\01')
            logger.info(
                f'Server is closing, reject connection from: {client_ip}'
            )
            return

        await conn.connect()

        work_id = uuid4().hex

        logger.info(
            f'{work_id} - Client connected, connection from {client_ip}')

        beta = await work_gen.get()

        if beta is None:
            writer.write(b'\01')
            await writer.drain()
            writer.close()
            logger.info(f'{work_id} - No work to assign.')
            await conn.disconnect()
            return

        writer.write(b'\00')
        await writer.drain()

        config = CONFIG_TEMPLATE.copy()
        config['memory'] = beta

        writer.write(work_id.encode('utf-8'))

        _config = cast(str, yaml.dump(config)).encode('utf-8')
        writer.write(len(_config).to_bytes(4, 'big'))
        writer.write(_config)
        await writer.drain()

        logger.info(f'{work_id} - Assigned work, {beta=}')

        try:
            logger.info(f'{work_id} - Waiting for work to complete.')
            await asyncio.wait_for(reader.read(1), 60 * 10)
        except asyncio.TimeoutError:
            writer.write(b'\01')
            logger.warning(f'{work_id} - Work timed out.')
            await work_gen.work_timeouted(beta)
        else:
            try:
                writer.write(b'\00')
                name_len = int.from_bytes(await reader.read(1), 'big')
                file_name = (await reader.read(name_len)).decode('utf-8')
                data = await reader.read(-1)

                out_file = out_dir / file_name
                out_file.parent.mkdir(exist_ok=True, parents=True)

                out_file.write_bytes(data)

                logger.info(
                    f'{work_id} - Work completed, saved to file {out_file}'
                )
                await work_gen.work_completed(beta)
            except Exception as e:
                logger.error(f'{work_id} - Exception: {e}')
                try:
                    if out_file.exists():
                        out_file.unlink()
                except Exception:
                    pass
                finally:
                    await work_gen.work_timeouted(beta)
                    await conn.disconnect()

        writer.close()
        await writer.wait_closed()

        await conn.disconnect()

        if not (conn.is_closed() or await work_gen.are_values_left()):
            logger.info(
                f'{work_id} - There are no more values to assign. '
                'Starting to close the server.'
            )
            conn.close()

    return _handle_request


# src: https://docs.python.org/3/library/asyncio-stream.html
@logger.catch
async def server(out_dir: Path) -> None:
    work_gen = WorkGenerator(START, END, STEP, NUM_OF_SAMPLES)
    close_server = asyncio.Event()

    conn = Connections(close_server)

    serv = await asyncio.start_server(
        handle_request(out_dir, conn, work_gen),
        '0.0.0.0',
        os.environ.get('DLA_PORT', 1025)
    )

    addr = serv.sockets[0].getsockname()  # type: ignore
    logger.info(f"Serving at: {addr}")

    await close_server.wait()

    while True:
        if not await conn.are_connections_left():
            break
        logger.info('Waiting for all connections to end.')
        await asyncio.sleep(10)

    serv.close()
    await serv.wait_closed()
    logger.info('Server closed.')


if __name__ == '__main__':
    asyncio.run(server(Path('./out')), debug=True)
