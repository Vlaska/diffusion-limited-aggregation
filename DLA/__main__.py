from __future__ import annotations

import sys
from functools import partial
from typing import Final, List, Tuple, TypeVar, Union, cast

import numpy as np
import numpy.typing as npt
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time

# from .walker import Walker

Vec = npt.ArrayLike
RGB = Tuple[int, int, int]

BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
GREEN: Final[RGB] = (0, 255, 0)
FPS: Final[int] = 30
WINDOW_SIZE: Final[Tuple[int, int]] = (1000, 1000)


def random_in_range(
    a: float,
    b: float,
    shape: Union[Vec, Tuple[float, ...]]
) -> Vec:
    return (b - a) * np.random.random_sample(shape) + a


class WalkerPopulation:
    def __init__(self, size: int) -> None:
        pos = np.array([
            random_in_range(0, WINDOW_SIZE[0], (size, )),
            random_in_range(0, WINDOW_SIZE[1], (size, )),
        ])
        self.pos = np.transpose(pos)
        self.size = size
        self.stuck = np.zeros(size, np.bool8)

    def walk(self):
        self.pos = self.pos + random_in_range(-5, 5, (self.size, 2))
        self.pos[:, 0] = np.clip(self.pos[:, 0], 0, WINDOW_SIZE[0])
        self.pos[:, 1] = np.clip(self.pos[:, 1], 0, WINDOW_SIZE[1])

    def __iter__(self):
        return iter(self.pos)


T = TypeVar('T', bound=WalkerPopulation, contravariant=True)


class StuckWalkers(WalkerPopulation):
    def __init__(self, walkers: T, start_pos: Vec) -> None:
        self.size = walkers.pos.shape[0] + 1
        self.pos = np.empty((self.size, 2))
        self.pos[0] = start_pos
        self.stuck = np.zeros(self.size, dtype=np.bool8)
        self.stuck[0] = True
        self.filled = 1

    def walk(self):
        raise NotImplementedError


class Walker(WalkerPopulation):
    def __init__(self):
        super().__init__(1)

    @classmethod
    def new(cls, pos: Vec) -> Walker:
        out = cls()
        out.pos[0, :] = pos
        return out


walkers: List[Walker] = []
walker_population: WalkerPopulation
stuck_points: List[Walker] = []


stuck_points.append(
    Walker.new(np.array((WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)))
)


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return (screen, clock)


def render(surface: surface.Surface):
    global walker_population
    surface.fill(BLACK)

    for i in stuck_points:
        draw.circle(surface, GREEN, cast(Tuple[float, float], i.pos[0]), 1)

    # for _ in range(500):
        # walker_population.walk()
    walker_population.walk()

    for i in walker_population:
        draw.circle(surface, WHITE, cast(Tuple[float, float], i), 1)

    # for i in walkers:
    #     for j in range(100):
    #         i.walk()
    #     draw.circle(surface, WHITE, cast(Tuple[float, float], i.pos), 1)

    display.flip()


def main():
    global walkers
    global walker_population
    walker_population = WalkerPopulation(0)
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
            walker_population = WalkerPopulation(1000)
        #     walkers.append(Walker.new())

        render(surface)


if __name__ == '__main__':
    main()
