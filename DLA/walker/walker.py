from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Iterator, Tuple, cast

import numpy as np

from DLA import RGB, WHITE, Vec, config

from .config import RADIUS

USE_PYGAME: Final[bool] = config['use_pygame']

if USE_PYGAME or TYPE_CHECKING:
    from pygame import draw as draw
    from pygame import surface as surface


class Walker:
    color: RGB = WHITE

    def __init__(self, size: int) -> None:
        self.pos: np.ndarray = np.empty((size, 2), dtype=np.double)
        self.size = size

    # region Abstract Methods
    def walk(self) -> None:
        raise NotImplementedError

    def is_stuck(self, other: Any) -> None:
        raise NotImplementedError
    # endregion

    # region Magic Methods
    def __iter__(self) -> Iterator[np.ndarray]:
        return iter(self.pos)

    def __getitem__(self, i: Any) -> np.ndarray:
        return self.pos[i]

    def __setitem__(self, i: Any, value: Any) -> None:
        self.pos[i] = value
    #endregion

    # region Pygame
    if USE_PYGAME:
        def draw(self, surface_: surface.Surface) -> None:
            for i in self:
                if not np.isnan(i[0]):
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
    else:
        def draw(self, surface_: surface.Surface) -> None: ...

        @staticmethod
        def draw_circle(
            surface_: surface.Surface,
            center: Vec,
            color: RGB
        ) -> None: ...
    # endregion
