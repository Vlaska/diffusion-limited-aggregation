from __future__ import annotations

import sys
from functools import partial
from typing import Final, List, Tuple, Union, cast

import numpy as np
import numpy.typing as npt
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time

Vec = npt.DTypeLike

BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
WHITE: Final[Tuple[int, int, int]] = (255, 255, 255)
FPS: Final[int] = 30
WINDOW_SIZE: Final[Tuple[int, int]] = (800, 600)


def random_in_range(
    a: float,
    b: float,
    shape: Union[Vec, Tuple[float, ...]]
) -> Vec:
    return (b - a) * np.random.random_sample(*shape) + a


class Walker:
    def __init__(self, pos: Vec):
        self.pos = np.array(pos)

    def walk(self):
        self.pos = self.pos + self.brownian()
        self.pos[0] = np.clip(self.pos[0], 0, WINDOW_SIZE[0])
        self.pos[1] = np.clip(self.pos[1], 0, WINDOW_SIZE[1])

    brownian = partial(random_in_range, a=-5, b=5, shape=(2, ))

    @classmethod
    def new(cls) -> Walker:
        pos = np.concatenate([
            random_in_range(0, WINDOW_SIZE[0], (1, )),
            random_in_range(0, WINDOW_SIZE[1], (1, )),
        ])

        return cls(pos)


walkers: List[Walker] = []
stuck_points: List[Walker] = []


stuck_points.append(Walker((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)))


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return (screen, clock)


def render(surface: surface.Surface):
    surface.fill(BLACK)

    for i in stuck_points:
        draw.circle(surface, WHITE, cast(Tuple[float, float], i.pos), 1)

    for i in walkers:
        for j in range(100):
            i.walk()
        draw.circle(surface, WHITE, cast(Tuple[float, float], i.pos), 1)

    display.flip()


def main():
    global walkers
    surface, clock = init()

    while True:
        clock.tick(FPS)

        for event in events.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            sys.exit(0)
        elif keys[pygame.K_SPACE]:
            walkers.append(Walker.new())

        render(surface)


if __name__ == '__main__':
    main()
