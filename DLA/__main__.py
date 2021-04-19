from __future__ import annotations

import sys
from functools import partial
from typing import Any, Final, Iterator, List, NoReturn, Tuple, Type, TypeVar, Union, cast

import numpy as np
import numpy.typing as npt
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time

from loguru import logger
from numpy import ma

logger.add("logs/{time}.log", rotation="5MB",
           format="{time} | {level} | {message}")

# from .walker import Walker

Vec = npt.ArrayLike
RGB = Tuple[int, int, int]

RADIUS: Final[float] = 5.0
BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
PINK: Final[RGB] = (255, 0, 255)
RED: Final[RGB] = (255, 0, 0)
GREEN: Final[RGB] = (0, 255, 0)
FPS: Final[int] = 30
WINDOW_SIZE: Final[Tuple[int, int]] = (200, 200)
SCREEN_CENTER: Final[Tuple[float, float]] = cast(
    Tuple[float, float], tuple(i / 2 for i in WINDOW_SIZE))
NUM_OF_POINTS: Final[int] = 50


def random_in_range(
    a: float,
    b: float,
    shape: Union[Vec, Tuple[float, ...]]
) -> Vec:
    return (b - a) * np.random.random_sample(shape) + a


class Walker:
    color: RGB = WHITE
    # stuck_value: bool = True

    def __init__(self, size: int) -> None:
        self.pos: ma.MaskedArray = ma.empty((size, 2), dtype=np.double)
        # self.stuck = np.zeros(size, dtype=np.bool8)
        self.size = size

    def __iter__(self) -> Iterator[Vec]:
        t = self.pos.compressed()
        return iter(t.reshape((t.shape[0] // 2, 2)))
        # return iter(self.pos)

    def walk(self) -> None:
        raise NotImplementedError

    def draw(self, surface: surface.Surface) -> None:
        for i in self:
            self.draw_circle(surface, i, self.color)

    def draw_point(self, surface: surface.Surface, index: int, color: RGB = RED) -> None:
        self.draw_circle(surface, self[index], color)

    @staticmethod
    def draw_circle(surface: surface.Surface, center: Vec, color: RGB) -> None:
        draw.circle(
            surface,
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
        return np.sum(v * v, axis=1)  # type: ignore


class StuckWalkers(Walker):
    color: RGB = GREEN
    # stuck_value: bool = False

    def __init__(self, walkers: Walker, start_pos: Vec) -> None:
        super().__init__(walkers.size + 1)
        self.pos[1:] = ma.masked
        self.pos[0] = start_pos
        # self.stuck[0] = True
        self.filled = 1

    def __iter__(self) -> Iterator[Vec]:
        return iter(self.pos.compressed().reshape((self.filled, 2)))

    def does_collide(self, point: Vec) -> bool:
        diffs: np.ndarray = np.abs(self.pos - point)
        t = self.squared_distance(diffs) < (4 * RADIUS * RADIUS)
        r = diffs[t].compressed()
        stuck_pos = r.reshape((r.shape[0] // 2, 2))
        try:
            _ = stuck_pos[0]
        except IndexError:
            return False
        else:
            # print(point, _, self.squared_distance(_.reshape(1, 2)))
            logger.debug(f"Point to add: {point}")
            return True

    def add_stuck(self, new_point: Vec) -> None:
        logger.debug(f"Added point:  {new_point}")
        # self.stuck[self.filled] = True
        self.pos[self.filled] = new_point
        self.filled += 1


class WalkerPopulation(Walker):
    def __init__(self, size: int) -> None:
        super().__init__(size)
        self.pos[:, 0] = random_in_range(0, WINDOW_SIZE[0], (size, ))
        self.pos[:, 1] = random_in_range(0, WINDOW_SIZE[1], (size, ))

    def walk(self) -> None:
        self.pos = self.pos + random_in_range(-5, 5, (self.size, 2))
        self.pos[:, 0] = np.clip(self.pos[:, 0], 0, WINDOW_SIZE[0])
        self.pos[:, 1] = np.clip(self.pos[:, 1], 0, WINDOW_SIZE[1])

    def pass_to_stuck(self, point: Vec, other: StuckWalkers) -> None:
        other.add_stuck(point)

    def is_stuck(self, other: StuckWalkers) -> None:
        # removed_points: List[int] = []
        # removed: List[Vec] = []
        for i, v in enumerate(self.pos):
            if not v.mask.any() and other.does_collide(v):
                self.pass_to_stuck(v, other)
                self[i] = ma.masked
                # removed.append(v)
                # removed_points.append(i)

        # if removed:
            # logger.debug(f"Points to remove: {list(removed)}")
            # logger.debug(f"Removed points:   {self[~self.stuck][removed_points]}")
        # self.stuck[removed_points] = True
        # self.stuck[~self.stuck][removed_points] = True


walker_population: WalkerPopulation = WalkerPopulation(0)
stuck_points: StuckWalkers = StuckWalkers(walker_population, SCREEN_CENTER)


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return (screen, clock)


def render(surface: surface.Surface) -> None:
    global walker_population
    surface.fill(BLACK)

    stuck_points.draw(surface)

    # for _ in range(15):
    #     walker_population.walk()
    walker_population.walk()
    walker_population.is_stuck(stuck_points)

    walker_population.draw(surface)

    display.flip()


def main() -> NoReturn:
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
            walker_population = WalkerPopulation(NUM_OF_POINTS)
            stuck_points = StuckWalkers(walker_population, SCREEN_CENTER)

        render(surface)


if __name__ == '__main__':
    main()
