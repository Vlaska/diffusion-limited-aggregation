from __future__ import annotations

from typing import Final, Iterable

import numpy as np
from numpy import NaN

from DLA import Vec
from DLA.config import (ALPHA, BETA, PUSH_OUT_TRIES, RADIUS, REGENERATE_AFTER,
                        WINDOW_SIZE)

from .particles_base import ParticlesBase
from .stuck_particles import StuckParticles
from .utils import random_in_range

BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = WINDOW_SIZE - RADIUS


class WalkingParticles(ParticlesBase):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, :] = random_in_range(BORDER_U_L, BORDER_D_R, (size, 2))
        self.last_step: np.ndarray = np.zeros((size, 2))
        self.last_regen = 0

    @classmethod
    def load_for_render(cls, particles: Iterable[Vec]) -> WalkingParticles:
        obj = cls(0)
        obj.pos = np.array(particles)
        obj.size = obj.pos.shape[0]
        return obj

    def walk(self) -> None:
        self.last_step = (
            BETA * self.last_step +
            ALPHA * np.random.standard_normal((self.size, 2))
        )

    def finish_walk(self) -> None:
        self.pos += self.last_step
        out_of_main_plain = ~((BORDER_U_L < self.pos) &
                              (self.pos < BORDER_D_R))
        self.last_step[out_of_main_plain] *= -1
        np.clip(
            self.pos,
            BORDER_U_L,
            BORDER_D_R,
            out=self.pos
        )

    def try_to_push_out(
        self,
        free_particle: Vec,
        last_step: Vec,
        time: float,
        other: StuckParticles
    ) -> None:
        for _ in range(PUSH_OUT_TRIES):
            free_particle = free_particle + last_step * time
            time = other.does_collide(free_particle, last_step)
            if time >= 0:
                break

        self.pass_to_stuck(free_particle, last_step, 0, other)

    @staticmethod
    def pass_to_stuck(
        point: Vec,
        step: Vec,
        time: float,
        other: StuckParticles
    ) -> None:
        other.add_stuck(point + step * time)

    def _is_stuck(self, other: StuckParticles) -> bool:
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

    def is_stuck(self, other: StuckParticles) -> None:
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

    def update(self, other: StuckParticles) -> None:
        self.walk()
        self.is_stuck(other)
        self.finish_walk()
