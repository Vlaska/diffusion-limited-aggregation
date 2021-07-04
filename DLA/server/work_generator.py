from __future__ import annotations

import asyncio
import pickle
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import yaml
from loguru import logger

from DLA.server import config_dict


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
        self.num_of_samples_per_memory = num
        self.to_distribute: Dict[float, int] = {
            i: num for i in tmp
        }
        self.waiting_for_results: Dict[float, int] = {
            i: 0 for i in tmp
        }
        self.num_of_done_works = 0
        self.state_loaded_from_file = False

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
            self.save_state()

    async def work_timed_out(self, val: float) -> None:
        async with self.lock:
            self.to_distribute[val] += 1
            self.waiting_for_results[val] -= 1

    def save_state(self) -> None:
        data = pickle.dumps(self.to_distribute)
        (
            self.state_folder / f'{self.num_of_done_works}.state'
        ).write_bytes(data)
        self.num_of_done_works += 1

    def try_load_saved_state(self, out_dir: Path) -> None:
        saved_state_folder = out_dir / 'state'
        if not saved_state_folder.exists():
            logger.info('No states were found.')
            return

        try:
            config_data = yaml.full_load(
                (saved_state_folder / 'config.yml').read_text('utf-8')
            )
        except FileNotFoundError:
            logger.info('Last config doesn\'t exists.')
            return

        if config_data != config_dict:
            logger.warning(
                'Current configuration doesn\'t match last one. '
                'Reseting state.'
            )
            return

        sorted_saved_state_files = sorted(
            saved_state_folder.glob('*.state'),
            key=lambda x: int(x.stem)
        )

        if not len(sorted_saved_state_files):
            logger.info('No states were found.')
            return

        last_state = sorted_saved_state_files[-1]
        state_data: Dict[float, int] = pickle.loads(
            last_state.read_bytes()
        )

        self.to_distribute = state_data
        self.state_loaded_from_file = True
        self.num_of_done_works = int(last_state.stem) + 1

        logger.info(
            'Successfully loaded last state. '
            f'State: {self.to_distribute}, '
            f'id of state: {self.num_of_done_works - 1}'
        )

    def set_up_state_saving(self, out_dir: Path) -> None:
        self.state_folder = out_dir / 'state'

        if self.state_loaded_from_file:
            return

        self.clean_states(self.state_folder)

        self.state_folder.mkdir(parents=True)

        (self.state_folder / 'config.yml').write_text(yaml.dump(config_dict))
        logger.info('Saved current configuration.')

    @staticmethod
    def clean_states(state_folder: Path) -> None:
        if state_folder.exists():
            shutil.rmtree(state_folder)
            logger.info('Removed states folder.')

    def configure(self, out_dir: Path) -> None:
        self.try_load_saved_state(out_dir)
        self.set_up_state_saving(out_dir)

    def get_missing_works(self, out_dir: Path) -> None:
        logger.info('Checking for missing work files.')
        data_files = out_dir.glob('*.pickle')
        loaded_memory_values = [
            pickle.loads(i.read_bytes())['memory'] for i in data_files
        ]
        missing_memory_values = {
            k: self.num_of_samples_per_memory - v
            for k, v in Counter(loaded_memory_values).items()
            if v < self.num_of_samples_per_memory
        }
        self.to_distribute = missing_memory_values
