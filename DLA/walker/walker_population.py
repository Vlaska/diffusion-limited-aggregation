from __future__ import annotations

from typing import Final

import numpy as np
from DLA import Vec, config
from DLA.utils import correct_circle_pos
from numpy import NaN

from .stuck_walkers import StuckWalkers
from .utils import random_in_range
from .walker import Walker

PUSH_OUT_TRIES: Final[int] = config['push_out_tries']
WINDOW_SIZE: Final[float] = config['window_size']
RADIUS: Final[float] = config['point_radius']
BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = config['window_size'] - RADIUS


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, :] = random_in_range(0, WINDOW_SIZE, (size, 2))
        self.last_step: np.ndarray

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
        eq_dist: bool,
        step: Vec,
        other: StuckWalkers
    ) -> None:
        tries = PUSH_OUT_TRIES
        while not (eq_dist or point is None) and tries:
            point = correct_circle_pos(
                point,
                step,
                colliding,
                RADIUS
            )
            colliding, eq_dist = other.does_collide(point)  # type: ignore
            tries -= 1
        other.add_stuck(point)

    def _is_stuck(self, other: StuckWalkers) -> bool:
        for i, v in enumerate(self.pos):
            if not np.isnan(v[0]):
                colliding, eq_dist = other.does_collide(v)
                if colliding is not None:
                    self.pass_to_stuck(
                        v, colliding, eq_dist, self.last_step[i], other
                    )
                    self[i] = NaN
                    return True
        return False

    def is_stuck(self, other: StuckWalkers) -> None:
        while self._is_stuck(other):
            pass
