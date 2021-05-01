from __future__ import annotations

from typing import Iterator, Optional, TYPE_CHECKING

import numpy as np
# from loguru import logger
from numpy import ma

from DLA import GREEN, Vec, RGB
from .config import RADIUS
from .walker import Walker

if TYPE_CHECKING:
    from .walker_population import WalkerPopulation
    from DLA.plane import Plane


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
        self.pos[1:] = ma.masked
        self.pos[0] = start_pos
        self.filled = 1
        self._plane = plane

    def __iter__(self) -> Iterator[Vec]:
        return iter(self.pos.compressed().reshape((self.filled, 2)))

    def does_collide(self, point: Vec) -> bool:
        diffs: np.ndarray = np.abs(self.pos - point)
        t = self.squared_distance(diffs) < (4 * RADIUS * RADIUS)
        r = diffs[t].compressed()
        stuck_pos = r.reshape((r.shape[0] // 2, 2))
        try:
            _ = stuck_pos[0]
        except IndexError:
            return False
        else:
            # logger.debug(f"Point to add: {point}")
            return True

    def add_stuck(self, new_point: Vec) -> None:
        # logger.debug(f"Added point:  {new_point}")
        self.pos[self.filled] = new_point
        self._plane.add_point(self.filled)
        self.filled += 1
