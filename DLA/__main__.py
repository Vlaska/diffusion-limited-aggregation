from __future__ import annotations

import sys
from typing import Final, NoReturn, Tuple, cast

import numpy as np
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.font as font
import pygame.key
import pygame.mouse as mouse
import pygame.surface as surface
import pygame.time as time
from loguru import logger

from DLA import BLACK, GREEN, WHITE, config, plane
from DLA.plane.dimension import Dimension
from DLA.types import Vec2

logger.add("logs/splitter - {time}.log", rotation="5MB",
           format="{time} | {level} | {message}")

FPS: Final[int] = 60
WINDOW_SIZE: Final[Tuple[int, int]] = (
    config['window_size'], config['window_size']
)
SCREEN_CENTER: Final[Vec2] = cast(
    Vec2, tuple(i / 2 for i in WINDOW_SIZE)
)
MIN_BOX_SIZE: Final[float] = 64

p = plane.Plane.new()
points = np.empty((1000, 2), dtype=np.double)


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return screen, clock


def render(surface_: surface.Surface, font_: font.Font) -> None:
    p.draw(surface_)

    # mouse_pos = mouse.get_pos()
    # text_surface = font_.render(str(mouse_pos), True, WHITE)
    # text_rect = text_surface.get_rect()
    # text_rect.topleft = (mouse_pos[0] + 15, mouse_pos[1] + 15)
    # surface_.blit(text_surface, text_rect)


def print_dim():
    dim = Dimension(p)
    dim.count()
    print(dim)
    print(dim.dim())


def main() -> NoReturn:
    surface_, clock = init()
    mouse_click_pos = None
    font_ = font.SysFont('arial', 16)
    global p

    while True:
        clock.tick(FPS)

        for event in events.get():
            if event.type == pygame.QUIT:
                print_dim()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    p = plane.Plane.new()
            # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            #     mouse_click_pos = event.pos
            #     logger.debug(f"Clicked at: {mouse_click_pos}")
            #     p.split_at_point(mouse_click_pos)
            # elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            #     mouse_click_pos = None

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            print_dim()
            sys.exit(0)

        p.update()

        surface_.fill(BLACK)

        render(surface_, font_)

        # if mouse_click_pos:
        #     mouse_click_pos = mouse.get_pos() or mouse_click_pos
        #     draw.circle(surface_, GREEN, mouse_click_pos, 1)

        display.flip()


if __name__ == '__main__':
    main()
