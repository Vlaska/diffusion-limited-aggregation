from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator

import numpy as np

from DLA import GREEN, RGB, Vec, Vec2
from DLA.config import NUM_OF_PARTICLES, PARTICLE_PLANE_SIZE, RADIUS
from DLA.utils import get_collision_time

from .particles_base import ParticlesBase

if TYPE_CHECKING:
    from DLA.plane.base_plane import BasePlane

    from .walking_particles import WalkingParticles


class StuckParticles(ParticlesBase):
    color: RGB = GREEN
    _plane: BasePlane

    def __init__(
        self,
        walkers: WalkingParticles,
        start_pos: Vec2,
        plane: BasePlane
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

    def does_collide(self, point: Vec, move_vec: Vec) -> float:
        return get_collision_time(
            self._plane, PARTICLE_PLANE_SIZE, point, move_vec, RADIUS
        )

    def add_stuck(self, new_point: Vec) -> None:
        self.pos[self.filled] = new_point
        self._plane.add_point(self.filled)
        self.filled += 1

    def is_complete(self) -> bool:
        return self.filled > NUM_OF_PARTICLES

    @classmethod
    def load_for_render(
        cls,
        walkers: WalkingParticles,
        particles: Iterable[Vec]
    ) -> StuckParticles:
        obj = cls(walkers, (0, 0), None)  # type: ignore
        obj.pos = np.array(particles)
        obj.size = obj.pos.shape[0]
        obj.filled = obj.size
        return obj
