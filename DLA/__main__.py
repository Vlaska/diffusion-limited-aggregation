from __future__ import annotations

import sys
from functools import partial
from typing import Final, Iterator, List, Tuple, TypeVar, Union, cast

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
SCREEN_CENTER: Final[Tuple[float, float]] = cast(
    Tuple[float, float], tuple(i / 2 for i in WINDOW_SIZE))


def random_in_range(
    a: float,
    b: float,
    shape: Union[Vec, Tuple[float, ...]]
) -> Vec:
    return (b - a) * np.random.random_sample(shape) + a


class Walker:
    color: RGB = WHITE

    def __init__(self, size: int) -> None:
        self.pos = np.empty((size, 2), dtype=np.double)
        self.stuck = np.zeros(size, dtype=np.bool8)
        self.size = size

    def __iter__(self) -> Iterator[Vec]:
        return iter(self.pos[~self.stuck])

    def walk(self):
        raise NotImplementedError

    def draw(self, surface: surface.Surface) -> None:
        for i in self:
            draw.circle(surface, self.color, cast(Tuple[float, float], i), 1)


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, 0] = random_in_range(0, WINDOW_SIZE[0], (size, ))
        self.pos[:, 1] = random_in_range(0, WINDOW_SIZE[1], (size, ))

    def walk(self):
        self.pos = self.pos + random_in_range(-5, 5, (self.size, 2))
        self.pos[:, 0] = np.clip(self.pos[:, 0], 0, WINDOW_SIZE[0])
        self.pos[:, 1] = np.clip(self.pos[:, 1], 0, WINDOW_SIZE[1])


T = TypeVar('T', bound=WalkerPopulation, contravariant=True)


class StuckWalkers(WalkerPopulation):
    color: RGB = GREEN

    def __init__(self, walkers: T, start_pos: Vec) -> None:
        super().__init__(walkers.size + 1)
        self.pos[0] = start_pos
        self.stuck[0] = True
        self.filled = 1

    def __iter__(self) -> Iterator[Vec]:
        return iter(self.pos[self.stuck])


walker_population: WalkerPopulation = WalkerPopulation(0)
stuck_points: StuckWalkers = StuckWalkers(walker_population, SCREEN_CENTER)


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

    stuck_points.draw(surface)

    # for _ in range(15):
    #     walker_population.walk()
    walker_population.walk()

    walker_population.draw(surface)

    display.flip()


def main():
    global walker_population
    global stuck_points
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
            stuck_points = StuckWalkers(walker_population, SCREEN_CENTER)

        render(surface)


if __name__ == '__main__':
    main()
