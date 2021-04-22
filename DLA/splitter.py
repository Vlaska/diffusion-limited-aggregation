from __future__ import annotations

from functools import cached_property
import sys
from typing import Any, Final, Iterator, List, NoReturn, Tuple, Union, cast

import numpy as np
import numpy.typing as npt
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time
import pygame.mouse as mouse

from loguru import logger

logger.add("logs/splitter - {time}.log", rotation="5MB",
           format="{time} | {level} | {message}")


Vec = npt.ArrayLike
RGB = Tuple[int, int, int]

WINDOW_WIDTH_AND_HEIGHT: Final[int] = 1024
RADIUS: Final[float] = 5.0
BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
PINK: Final[RGB] = (255, 0, 255)
RED: Final[RGB] = (255, 0, 0)
GREEN: Final[RGB] = (0, 255, 0)
FPS: Final[int] = 60
WINDOW_SIZE: Final[Tuple[int, int]] = (
    WINDOW_WIDTH_AND_HEIGHT, WINDOW_WIDTH_AND_HEIGHT
)
SCREEN_CENTER: Final[Tuple[float, float]] = cast(
    Tuple[float, float], tuple(i / 2 for i in WINDOW_SIZE)
)
MIN_BOX_SIZE: Final[float] = 64


class Plane:
    def __init__(
        self,
        start: Tuple[float, float],
        size: Tuple[float, float],
    ) -> None:
        self.left, self.top = start
        self.width, self.height = size
        self.rect = pygame.Rect(self.left, self.top, self.width, self.height)
        self.children: List[Plane] = []

    @classmethod
    def new(cls) -> Plane:
        return cls((0, 0), WINDOW_SIZE)

    def draw(self, surface: surface.Surface) -> None:
        draw.rect(surface, WHITE, self.rect, 1)
        for i in self.children:
            i.draw(surface)

    def split(self) -> None:
        if self.children:
            # logger.debug("Split children")
            if self.width > MIN_BOX_SIZE:
                for i in self.children:
                    i.split()
        else:
            # logger.debug("Split self")
            new_width = self.width / 2
            new_height = self.height / 2
            new_size = (new_width, new_height)
            lefts_and_tops = [
                (self.left, self.top),
                (self.left, self.top + new_height),
                (self.left + new_width, self.top),
                (self.left + new_width, self.top + new_height),
            ]
            self.children.extend(Plane(i, new_size) for i in lefts_and_tops)


p = Plane.new()


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation - Splitter")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return (screen, clock)


def render(surface: surface.Surface) -> None:
    surface.fill(BLACK)

    p.draw(surface)

    display.flip()


def main() -> NoReturn:
    surface, clock = init()
    mouse_click_pos = None
    split_event = False

    while True:
        clock.tick(FPS)

        for event in events.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                split_event = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_click_pos = None

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            sys.exit(0)

        if split_event:
            p.split()
            split_event = False
        # if mouse.get_pressed(pygame.)

        render(surface)

        if mouse_click_pos:
            # print(mouse_click_pos)
            display.flip()
            mouse_click_pos = mouse.get_pos() or mouse_click_pos
            draw.circle(surface, GREEN, mouse_click_pos, 1)
            display.flip()


if __name__ == '__main__':
    main()