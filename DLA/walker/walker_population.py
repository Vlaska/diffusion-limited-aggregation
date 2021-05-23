from __future__ import annotations

from typing import Final

import numpy as np
from numpy import NaN

from DLA import Vec
from DLA.config import (ALPHA, BETA, PUSH_OUT_TRIES, RADIUS, REGENERATE_AFTER,
                        WINDOW_SIZE)
from DLA.utils import correct_circle_pos

from .stuck_walkers import StuckWalkers
from .utils import random_in_range
from .walker import Walker

BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = WINDOW_SIZE - RADIUS


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, :] = random_in_range(BORDER_U_L, BORDER_D_R, (size, 2))
        self.last_step: np.ndarray = np.zeros((size, 2))
        self.last_regen = 0

    def walk(self) -> None:
        # self.last_step = random_in_range(-5, 5, (self.size, 2))
        # self.last_step = ALPHA * np.random.standard_normal((self.size, 2))
        self.last_step = (
            BETA * self.last_step +
            ALPHA * np.random.standard_normal((self.size, 2))
        )

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
        # * replacement for tail recursion
        while self._is_stuck(other):
            pass

        self.regenerate_population()

    def regenerate_population(self):
        if self.last_regen >= REGENERATE_AFTER:
            mask = ~np.isnan(self.pos[:, 0])
            self.pos = self.pos[mask]
            self.last_step = self.last_step[mask]
            self.last_regen = -1
            self.size = self.pos.shape[0]
        self.last_regen += 1

    def update(self, other: StuckWalkers) -> None:
        self.walk()
        self.is_stuck(other)
