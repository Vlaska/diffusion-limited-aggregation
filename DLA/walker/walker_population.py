from __future__ import annotations

from typing import Final

import numpy as np
from numpy import NaN

from DLA import Vec
from DLA.config import (ALPHA, BETA, PUSH_OUT_TRIES, RADIUS, REGENERATE_AFTER,
                        WINDOW_SIZE)

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
        self.last_step = (
            BETA * self.last_step +
            ALPHA * np.random.standard_normal((self.size, 2))
        )

    def finish_walk(self) -> None:
        np.clip(
            self.pos + self.last_step,
            BORDER_U_L,
            BORDER_D_R,
            out=self.pos
        )

    def try_to_push_out(
        self,
        free_part: Vec,
        last_step: Vec,
        time: float,
        other: StuckWalkers
    ) -> None:
        for _ in range(PUSH_OUT_TRIES):
            free_part = free_part + last_step * time
            time = other.does_collide(free_part, last_step)
            if time >= 0:
                break

        self.pass_to_stuck(free_part, last_step, 0, other)

    @staticmethod
    def pass_to_stuck(
        point: Vec,
        step: Vec,
        time: float,
        other: StuckWalkers
    ) -> None:
        other.add_stuck(point + step * time)

    def _is_stuck(self, other: StuckWalkers) -> bool:
        for i, v in enumerate(self.pos):
            if not np.isnan(v[0]):
                t = other.does_collide(v, self.last_step[i])
                if t < 0:
                    self.try_to_push_out(v, self.last_step[i], t, other)
                    self[i] = NaN
                    return True
                elif t <= 1:
                    self.pass_to_stuck(
                        v, self.last_step[i], t, other
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
        self.finish_walk()
