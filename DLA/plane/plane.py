from __future__ import annotations

from typing import Final

import numpy as np
import pygame
from DLA import WHITE, Vec2, config
from loguru import logger
from pygame import draw
from pygame.surface import Surface

from .chunks import Chunks

WINDOW_WIDTH_AND_HEIGHT: Final[int] = config['window_size']
MIN_BOX_SIZE: Final[float] = config['min_box_size']


class Plane:
    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = start
        self.size = size
        self.rect = pygame.Rect(*self.start_pos, self.size, self.size)
        # self.chunks: List[Plane] = []
        self.chunks = Chunks(start, size)

    @classmethod
    def new(cls) -> Plane:
        return cls((0, 0), WINDOW_WIDTH_AND_HEIGHT)

    def draw(self, surface: Surface) -> None:
        draw.rect(surface, WHITE, self.rect, 1)
        for i in self.chunks:
            if i:
                i.draw(surface)

    def split(self) -> None:
        if self.chunks:
            # logger.debug("Split children")
            if self.size > MIN_BOX_SIZE:
                for i in self.chunks:
                    i.split()
        else:
            # logger.debug("Split self")
            halved_size = self.size / 2
            for i, co in enumerate(self.chunks.get_all_coords()):
                self.chunks[i] = Plane(co, halved_size)

    def split_at_point(self, point: Vec2 | np.ndarray) -> None:
        if self.size <= MIN_BOX_SIZE:
            return
        sub_chunks = self.chunks.get_chunks(point)
        logger.debug(f"Selected chunks: {tuple(sub_chunks.selected)}")
        for i, c in enumerate(sub_chunks):
            if not c:
                logger.debug(
                    "Created chunk at: "
                    f"{self.chunks.get_sub_coords(sub_chunks.chunk_index(i))} "
                    f"of size: {self.size / 2}"
                )
                sub_chunks[i] = c = Plane(
                    self.chunks.get_sub_coords(sub_chunks.chunk_index(i)),
                    self.size / 2
                )
            c.split_at_point(point)
            # add point ?
