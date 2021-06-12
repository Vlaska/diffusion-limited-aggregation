from __future__ import annotations

from DLA import Vec2
# from DLA.config import
from DLA.plane.base_plane import BasePlane


class ParticlePlane(BasePlane):
    def __init__(self, start: Vec2, size: float) -> None:
        super().__init__(start, size)
        self.parts = []

    def add_point(self, point: int) -> None:
        super().add_point(point)
        self.parts.append(point)
