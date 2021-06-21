from __future__ import annotations

from array import array

from DLA import Vec2
from DLA.config import SECOND_MIN_BOX_SIZE
from DLA.plane.indivisible_plane import IndivisiblePlane
from DLA.plane.plane_fullness import FullablePlane
from DLA.plane.sub_planes import SubPlane


class SubPlaneParticlesAndIndivisible(FullablePlane, SubPlane):
    _alt_plane_type = IndivisiblePlane
    _size_for_alt_plane_type = SECOND_MIN_BOX_SIZE


class ParticlePlane(FullablePlane):
    _new_plane_type = SubPlaneParticlesAndIndivisible

    def __init__(self, start: Vec2, size: float) -> None:
        super().__init__(start, size)
        self.parts: array[int] = array('I')

    def add_point(self, point: int) -> None:
        super().add_point(point)
        self.parts.append(point)
