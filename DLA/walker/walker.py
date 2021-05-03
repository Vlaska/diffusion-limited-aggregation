from __future__ import annotations

from typing import Iterator, cast, Tuple, Any

import numpy as np
from numpy import NaN
from pygame import surface as surface, draw as draw

from DLA import WHITE, RED, RGB, Vec
from .config import RADIUS


class Walker:
    color: RGB = WHITE

    def __init__(self, size: int) -> None:
        self.pos: np.ndarray = np.empty((size, 2), dtype=np.double)
        self.size = size

    def __iter__(self) -> Iterator[np.ndarray]:
        return iter(self.pos)

    def walk(self) -> None:
        raise NotImplementedError

    def draw(self, surface_: surface.Surface) -> None:
        for i in self:
            if i[0] is not NaN:
                self.draw_circle(surface_, i, self.color)

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
