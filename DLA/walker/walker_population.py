from __future__ import annotations

from typing import Final

import numpy as np
from DLA import Vec, config
from DLA.utils import correct_circle_pos
from numpy import NaN
from loguru import logger

from .stuck_walkers import StuckWalkers
from .utils import random_in_range
from .walker import Walker

WINDOW_SIZE: Final[float] = config['window_size']
RADIUS: Final[float] = config['point_radius']
BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = config['window_size'] - RADIUS

logger.add("logs/utils-{time}.log",
           format="{time} | {level} | {message}")


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, :] = random_in_range(0, WINDOW_SIZE, (size, 2))
        self.last_walk_vec: np.ndarray

    def walk(self) -> None:
        self.last_step = random_in_range(-5, 5, (self.size, 2))
        np.clip(
            self.pos + self.last_step,
            BORDER_U_L,
            BORDER_D_R,
            out=self.pos
        )

    @staticmethod
    def pass_to_stuck(
        point: Vec,
        colliding: Vec,
        step: Vec,
        other: StuckWalkers
    ) -> None:
        # ? Maybe check/push out multiple times, if particle is now colliding
        # ? with another solid particle
        receved_value = correct_circle_pos(
            point,
            step,
            colliding,
            RADIUS
        )
        logger.debug(f'Receved value: {tuple(receved_value)}')
        other.add_stuck(receved_value)

    def is_stuck(self, other: StuckWalkers) -> None:
        for i, v in enumerate(self.pos):
            if not np.isnan(v[0]):
                if (colliding := other.does_collide(v)) is not None:
                    self.pass_to_stuck(v, colliding, self.last_step[i], other)
                    self[i] = NaN
