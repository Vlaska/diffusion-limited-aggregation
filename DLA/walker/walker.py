from __future__ import annotations

from typing import Iterator, cast, Tuple, Any

import numpy as np
from numpy import ma
from pygame import surface as surface, draw as draw

from DLA import WHITE, RED, RGB, Vec
from .config import RADIUS


class Walker:
    color: RGB = WHITE

    def __init__(self, size: int) -> None:
        self.pos: ma.MaskedArray = ma.empty((size, 2), dtype=np.double)
        self.size = size

    def __iter__(self) -> Iterator[Vec]:
        t = self.pos.compressed()
        return iter(t.reshape((t.shape[0] // 2, 2)))

    def walk(self) -> None:
        raise NotImplementedError

    def draw(self, surface_: surface.Surface) -> None:
        for i in self:
            self.draw_circle(surface_, i, self.color)

    def draw_point(
        self,
        surface_: surface.Surface,
        index: int,
        color: RGB = RED
    ) -> None:
        self.draw_circle(surface_, self[index], color)

    @staticmethod
    def draw_circle(
        surface_: surface.Surface,
        center: Vec,
        color: RGB
    ) -> None:
        draw.circle(
            surface_,
            color,
            cast(Tuple[float, float], center),
            RADIUS
        )

    def is_stuck(self, other: Any) -> None:
        raise NotImplementedError

    def __getitem__(self, i: Any) -> np.ndarray:
        return self.pos[i]

    def __setitem__(self, i: Any, value: Any) -> None:
        self.pos[i] = value

    @staticmethod
    def squared_distance(v: np.ndarray) -> np.ndarray:
        return cast(np.ndarray, np.sum(v * v, axis=1))
