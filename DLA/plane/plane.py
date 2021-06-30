from __future__ import annotations

from typing import Dict, List, Type

import numpy as np
from DLA import Vec, Vec2
from DLA.config import (NUM_OF_PARTICLES, PARTICLE_PLANE_SIZE,
                        SECOND_MIN_BOX_SIZE, STARTING_POS, WINDOW_SIZE)
from DLA.exceptions import StopSimulation
from DLA.plane.base_plane import BasePlane
from DLA.plane.indivisible_plane import IndivisiblePlane
from DLA.plane.particle_plane import ParticlePlane
from DLA.plane.plane_fullness import FullablePlane, NotFullablePlane
from DLA.plane.sub_planes import SubPlane
from DLA.utils import one_subchunk_coords
from DLA.walker import StuckWalkers, WalkerPopulation


class SubPlanePlaneAndParticles(NotFullablePlane, SubPlane):
    _alt_plane_type = ParticlePlane
    _size_for_alt_plane_type = PARTICLE_PLANE_SIZE


class NeighbouringPlanes(FullablePlane, SubPlane):
    _alt_plane_type = IndivisiblePlane
    _size_for_alt_plane_type = SECOND_MIN_BOX_SIZE


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

    def __init__(self, start: Vec2, size: float) -> None:
        super().__init__(start, size)
        self.neighbours: List[NeighbouringPlanes] = []
        self.setupNeighbours()

    def setupNeighbours(self) -> None:
        tmp = self.size * 2
        self.neighbours.extend(
            NeighbouringPlanes(
                one_subchunk_coords(
                    np.array((-self.size, -self.size), dtype=np.double), tmp, i
                ), self.size
            ) for i in range(3)
        )
        self.neighbours.extend(
            NeighbouringPlanes(
                one_subchunk_coords(np.zeros(2, dtype=np.double), tmp, i),
                self.size
            ) for i in range(1, 4)
        )
        self.neighbours.extend((
            NeighbouringPlanes((self.size, -self.size), self.size),
            NeighbouringPlanes((-self.size, self.size), self.size),
        ))

    def update(self):
        self._walking_points.update(self._stuck_points)
        if self._stuck_points.is_complete():
            raise StopSimulation

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
