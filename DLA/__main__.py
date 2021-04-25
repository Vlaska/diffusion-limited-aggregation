from __future__ import annotations

import sys
from typing import Final, NoReturn, Tuple, cast

import pygame
import pygame.display as display
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time
from loguru import logger

from DLA import config, BLACK
from DLA.walker import StuckWalkers, WalkerPopulation

logger.add("logs/{time}.log", rotation="5MB",
           format="{time} | {level} | {message}")

RADIUS: Final[float] = config['point_radius']
FPS: Final[int] = config['fps']
WINDOW_SIZE: Final[Tuple[int, int]] = cast(
    Tuple[int, int],
    (config['window_size'],) * 2
)
SCREEN_CENTER: Final[Tuple[float, float]] = cast(
    Tuple[float, float], tuple(i / 2 for i in WINDOW_SIZE))
NUM_OF_POINTS: Final[int] = config['num_of_points']

walker_population: WalkerPopulation = WalkerPopulation(0)
stuck_points: StuckWalkers = StuckWalkers(walker_population, SCREEN_CENTER)


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return screen, clock


def render(surface_: surface.Surface) -> None:
    global walker_population
    surface_.fill(BLACK)

    stuck_points.draw(surface_)

    # for _ in range(15):
    #     walker_population.walk()
    walker_population.walk()
    walker_population.is_stuck(stuck_points)

    walker_population.draw(surface_)

    display.flip()


def main() -> NoReturn:
    global walker_population
    global stuck_points
    walker_population = WalkerPopulation(0)
    surface_, clock = init()

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

        render(surface_)


if __name__ == '__main__':
    main()
