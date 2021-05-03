from __future__ import annotations

import sys
from typing import Final, NoReturn, Tuple

import numpy as np
import pygame
import pygame.display as display
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time

from DLA import BLACK, config, plane
from DLA.plane.dimension import Dimension


FPS: Final[int] = 60
WINDOW_SIZE: Final[Tuple[int, int]] = (
    config['window_size'], config['window_size']
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


def render(surface_: surface.Surface) -> None:
    p.draw(surface_)


def print_dim():
    dim = Dimension(p)
    dim.count()
    print(dim)
    print(dim.dim())


def main() -> NoReturn:
    surface_, clock = init()
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

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            print_dim()
            sys.exit(0)

        p.update()

        surface_.fill(BLACK)

        render(surface_)

        display.flip()


if __name__ == '__main__':
    main()
