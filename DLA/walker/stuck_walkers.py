from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

import numpy as np
from DLA import GREEN, RGB, Vec
from DLA.utils import squared_distance
from loguru import logger

from .config import RADIUS
from .walker import Walker

if TYPE_CHECKING:
    from DLA.plane import Plane

    from .walker_population import WalkerPopulation

logger.add("logs/utils-{time}.log", rotation="5MB",
           format="{time} | {level} | {message}")


class StuckWalkers(Walker):
    color: RGB = GREEN
    _plane: Plane

    def __init__(
        self,
        walkers: WalkerPopulation,
        start_pos: Vec,
        plane: Plane
    ) -> None:
        super().__init__(walkers.size + 1)
        self.pos[0] = start_pos
        self.filled = 1
        self._plane = plane

    def __iter__(self) -> Iterator[np.ndarray]:
        return iter(self.pos[:self.filled])

    @property
    def view(self) -> np.ndarray:
        return self.pos[:self.filled]

    def does_collide(self, point: Vec) -> Optional[Vec]:
        diffs: np.ndarray = np.abs(self.view - point)
        dist: np.ndarray = squared_distance(diffs)
        # t = dist < (4 * RADIUS * RADIUS)
        t = np.argmin(dist)
        # logger.debug(dist[t < 4 * RADIUS * RADIUS])
        stuck_pos = self.view[t]
        # if dist[t] > 4 * RADIUS * RADIUS:
        #     return None
        # return stuck_pos
        return None if dist[t] > 4 * RADIUS * RADIUS else stuck_pos
        # try:
        #     _ = stuck_pos[0]
        # except IndexError:
        #     return False
        # else:
        #     return True

    def add_stuck(self, new_point: Vec) -> None:
        logger.debug(f"Point to be added: {new_point}")
        self.pos[self.filled] = new_point
        logger.debug(f"Added point: {tuple(self.pos[self.filled])}")
        self._plane.add_point(self.filled)
        self.filled += 1
        if np.any(self.view == np.NaN):
            logger.debug("NaN found!")
            exit(1)
