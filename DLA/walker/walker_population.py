from __future__ import annotations

from DLA import Vec2
from typing import Final, cast

import numpy as np
from numpy import ma

from DLA import Vec, config
from .utils import random_in_range
from .stuck_walkers import StuckWalkers
from .walker import Walker


WINDOW_SIZE: Final[Vec2] = cast(Vec2, (config['window_size'], ) * 2)


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, 0] = random_in_range(0, WINDOW_SIZE[0], (size,))
        self.pos[:, 1] = random_in_range(0, WINDOW_SIZE[1], (size,))

    def walk(self) -> None:
        self.pos = self.pos + random_in_range(-5, 5, (self.size, 2))
        self.pos[:, 0] = np.clip(self.pos[:, 0], 0, WINDOW_SIZE[0])
        self.pos[:, 1] = np.clip(self.pos[:, 1], 0, WINDOW_SIZE[1])

    @staticmethod
    def pass_to_stuck(point: Vec, other: StuckWalkers) -> None:
        other.add_stuck(point)

    def is_stuck(self, other: StuckWalkers) -> None:
        for i, v in enumerate(self.pos):
            if not v.mask.any() and other.does_collide(v):
                self.pass_to_stuck(v, other)
                self[i] = ma.masked
