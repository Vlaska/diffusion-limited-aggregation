from __future__ import annotations

from typing import Final

import numpy as np
from DLA import Vec, config
from numpy import ma

from .stuck_walkers import StuckWalkers
from .utils import random_in_range
from .walker import Walker

WINDOW_SIZE: Final[float] = config['window_size']
RADIUS: Final[float] = config['point_radius']
BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = config['window_size'] - RADIUS


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, :] = random_in_range(0, WINDOW_SIZE, (size, 2))

    def walk(self) -> None:
        np.clip(
            self.pos + random_in_range(-5, 5, (self.size, 2)),
            BORDER_U_L,
            BORDER_D_R,
            out=self.pos
        )

    @staticmethod
    def pass_to_stuck(point: Vec, other: StuckWalkers) -> None:
        other.add_stuck(point)

    def is_stuck(self, other: StuckWalkers) -> None:
        for i, v in enumerate(self.pos):
            if not v.mask.any() and other.does_collide(v):
                self.pass_to_stuck(v, other)
                self[i] = ma.masked
