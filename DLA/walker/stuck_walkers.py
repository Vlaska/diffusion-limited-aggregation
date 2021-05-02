from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

import numpy as np

from DLA import GREEN, Vec, RGB
from DLA.utils import squared_distance
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
        self.pos[0] = start_pos
        self.filled = 1
        self._plane = plane

    def __iter__(self) -> Iterator[np.ndarray]:
        return iter(self.pos[:self.filled])

    @property
    def view(self) -> np.ndarray:
        return self.pos[:self.filled]

    def does_collide(self, point: Vec) -> bool:
        diffs: np.ndarray = np.abs(self.view - point)
        t = squared_distance(diffs) < (4 * RADIUS * RADIUS)
        stuck_pos = diffs[t]
        try:
            _ = stuck_pos[0]
        except IndexError:
            return False
        else:
            return True

    def add_stuck(self, new_point: Vec) -> None:
        self.pos[self.filled] = new_point
        self._plane.add_point(self.filled)
        self.filled += 1
