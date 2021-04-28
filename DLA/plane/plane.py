from __future__ import annotations

from typing import TYPE_CHECKING, Final, List

import numpy as np
import pygame
from DLA import WHITE, Vec2, config
from pygame import draw
from pygame.surface import Surface

from .chunks import Chunks

WINDOW_WIDTH_AND_HEIGHT: Final[int] = config['window_size']
MIN_BOX_SIZE: Final[float] = config['min_box_size']

if TYPE_CHECKING:
    from DLA.walker import StuckWalkers


class Plane:
    _stuck_points: StuckWalkers

    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = start
        self.size = size
        self.rect = pygame.Rect(*self.start_pos, self.size, self.size)
        self.chunks = Chunks(start, size)
        self._points: List[int] = []

    @classmethod
    def new(cls, stuck_points: StuckWalkers) -> Plane:
        cls._stuck_points = stuck_points

        obj = cls((0, 0), WINDOW_WIDTH_AND_HEIGHT)
        # for i in enumerate

        return obj

    def draw(self, surface: Surface) -> None:
        draw.rect(surface, WHITE, self.rect, 1)
        for i in self.chunks:
            if i:
                i.draw(surface)

    def split_at_point(self, point: Vec2 | np.ndarray) -> None:
        if self.size <= MIN_BOX_SIZE:
            return
        sub_chunks = self.chunks.get_chunks(point)
        for i, c in enumerate(sub_chunks):
            if not c:
                sub_chunks[i] = c = Plane(
                    self.chunks.get_sub_coords(sub_chunks.chunk_index(i)),
                    self.size / 2
                )
            c.split_at_point(point)
            # ? add point ?

    def __bool__(self) -> bool:
        return len(self._points) > 0

    def add_point(self, point: int) -> None:
        self._points.append(point)
