from __future__ import annotations

from typing import Dict, Iterable, Type, cast

import numpy as np

from DLA import Vec
from DLA.config import (NUM_OF_PARTICLES, STARTING_POS,
                        WINDOW_SIZE, PARTICLE_PLANE_SIZE)
from DLA.exceptions import StopSimulation
from DLA.plane.base_plane import BasePlane
from DLA.utils import one_subchunk_coords
from DLA.walker import StuckWalkers, WalkerPopulation
from DLA.plane.plane_fullness import NotFullablePlane
from DLA.plane.sub_planes import SubPlane
from DLA.plane.particle_plane import ParticlePlane


class SubPlanePlaneAndParticles(NotFullablePlane, SubPlane):
    _alt_plane_type = ParticlePlane
    _size_for_alt_plane_type = PARTICLE_PLANE_SIZE


class Plane(NotFullablePlane):
    """
    Sub planes assignment
    ┌───────┬───────┐
    │       │       │
    │   0   │   1   │
    │       │       │
    ├───────┼───────┤
    │       │       │
    │   2   │   3   │
    │       │       │
    └───────┴───────┘
    """

    _new_plane_type: Type[BasePlane] = SubPlanePlaneAndParticles

    def update(self):
        self._walking_points.update(self._stuck_points)
        if self._stuck_points.is_complete():
            raise StopSimulation

    def add_point(self, point: int) -> None:
        sub_planes = self._add_point(point)

        if sub_planes is None:
            return

        for i in sub_planes:
            cast(Plane, self._sub_planes[i]).add_point(point)

        if self.are_full():
            self.set_full()

    @classmethod
    def new(cls) -> Plane:
        obj = cls((0, 0), WINDOW_SIZE)

        BasePlane._walking_points = WalkerPopulation(NUM_OF_PARTICLES)
        BasePlane._stuck_points = StuckWalkers(
            cls._walking_points, STARTING_POS, obj
        )

        # * Method called at initialization of simulation;
        # * There is only one point present
        obj.add_point(0)

        return obj

    def get_data(self) -> Dict[str, Vec]:
        nan_mask = np.isnan(self._walking_points.pos)[:, 0]
        return {
            'stuck_particles': self._stuck_points[:self._stuck_points.filled],
            'free_particles': self._walking_points.pos[~nan_mask],
        }
