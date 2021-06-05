from __future__ import annotations

from typing import Dict, Iterable, Optional, Type, cast

import numpy as np

from DLA import Vec
from DLA.config import (NUM_OF_PARTICLES, SECOND_MIN_BOX_SIZE, STARTING_POS,
                        WINDOW_SIZE)
from DLA.exceptions import StopSimulation
from DLA.plane.base_plane import BasePlane
from DLA.plane.indivisible_plane import IndivisiblePlane
from DLA.utils import one_subchunk_coords
from DLA.walker import StuckWalkers, WalkerPopulation


class Plane(BasePlane):
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

    _new_plane_type_: Type[BasePlane]

    def update(self):
        self._walking_points.update(self._stuck_points)
        if self._stuck_points.is_complete():
            raise StopSimulation

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            if not self._sub_planes[i]:
                self._sub_planes[i] = self._new_plane_type(
                    one_subchunk_coords(self.start_pos, self.size, i),
                    self.size / 2
                )

    def add_point(self, point: int) -> None:
        sub_planes = self._add_point(point)

        if sub_planes is None:
            return

        for i in sub_planes:
            cast(Plane, self._sub_planes[i]).add_point(point)

        if self.are_full():
            self.set_full()

    @staticmethod
    def _check_is_full(v: Optional[BasePlane]) -> bool:
        return v and v.full  # type: ignore

    def are_full(self) -> bool:
        return self.full or all(
            self._check_is_full(self._sub_planes[i]) for i in range(4)
        )

    @property
    def _new_plane_type(self) -> Type[BasePlane]:
        try:
            return self._new_plane_type_
        except AttributeError:
            self._new_plane_type_ = (
                IndivisiblePlane
                if self.size / 2 == SECOND_MIN_BOX_SIZE else Plane
            )
            return self._new_plane_type_

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
