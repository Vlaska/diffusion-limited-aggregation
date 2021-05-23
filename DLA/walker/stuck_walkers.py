from __future__ import annotations

from typing import TYPE_CHECKING, Final, Iterator, Optional, Tuple

import numpy as np

from DLA import GREEN, RGB, Vec, Vec2
from DLA.config import EPSILON, RADIUS, RADIUS_CHECK, WINDOW_CENTER
from DLA.utils import dot_self, squared_distance

from .walker import Walker

if TYPE_CHECKING:
    from DLA.plane.base_plane import BasePlane

    from .walker_population import WalkerPopulation


SQUARED_PARTICLE_DISTANCE: Final[float] = 4 * RADIUS * RADIUS


class StuckWalkers(Walker):
    color: RGB = GREEN
    _plane: BasePlane
    radius: float

    def __init__(
        self,
        walkers: WalkerPopulation,
        start_pos: Vec2,
        plane: BasePlane
    ) -> None:
        super().__init__(walkers.size + 1)
        self.pos[0] = start_pos
        self.filled = 1
        self._plane = plane
        self.raw_radius = 0

    def __iter__(self) -> Iterator[np.ndarray]:
        return iter(self.pos[:self.filled])

    @property
    def view(self) -> np.ndarray:
        return self.pos[:self.filled]

    @property
    def raw_radius(self):
        return self._raw_radius

    @raw_radius.setter
    def raw_radius(self, value: float) -> None:
        self._raw_radius = value
        self.radius = (value + RADIUS_CHECK) ** 2

    def does_collide(self, point: Vec) -> Tuple[Optional[Vec], bool]:
        if dot_self(point - WINDOW_CENTER) > self.radius:
            return None, False

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

        if (dist := dot_self(new_point - WINDOW_CENTER)) > self.raw_radius:
            self.raw_radius = dist
