from __future__ import annotations

from typing import TYPE_CHECKING, Final, Iterator, Optional, Tuple

import numpy as np
from DLA import GREEN, RGB, Vec, config
from DLA.utils import squared_distance

from .config import RADIUS
from .walker import Walker

if TYPE_CHECKING:
    from DLA.plane import Plane
    from .walker_population import WalkerPopulation


SQUARED_PARTICLE_DISTANCE: Final[float] = 4 * RADIUS * RADIUS
EPSILON: Final[float] = config['epsilon']


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

    def does_collide(self, point: Vec) -> Tuple[Optional[Vec], bool]:
        diffs: np.ndarray = np.abs(self.view - point)
        dist: np.ndarray = squared_distance(diffs)

        t = np.argmin(dist)
        stuck_pos = self.pos[t]

        is_equal = -EPSILON <= dist[t] - SQUARED_PARTICLE_DISTANCE <= EPSILON

        return (
            None if dist[t] > SQUARED_PARTICLE_DISTANCE else stuck_pos,
            is_equal
        )

    def add_stuck(self, new_point: Vec) -> None:
        self.pos[self.filled] = new_point
        self._plane.add_point(self.filled)
        self.filled += 1
