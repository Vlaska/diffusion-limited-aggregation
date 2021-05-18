from __future__ import annotations

import sys
import signal
from gc import collect
from typing import Final, NoReturn, TYPE_CHECKING, Tuple
from beautifultable import BeautifulTable

from DLA import BLACK, config, plane
from DLA.plane.dimension import Dimension


# region Consts
FPS: Final[int] = 60
WINDOW_SIZE: Final[Tuple[int, int]] = (
    config['window_size'], config['window_size']
)
MIN_BOX_SIZE: Final[float] = 64
USE_PYGAME: Final[bool] = config['use_pygame']
# endregion

if USE_PYGAME or TYPE_CHECKING:
    import pygame
    import pygame.display as display
    import pygame.event as events
    import pygame.key
    import pygame.surface as surface
    import pygame.time as time

p = plane.Plane.new()


def print_dim():
    dim = Dimension(p)
    dim.count()

    tab = BeautifulTable(precision=6)
    tab.columns.header = ['Box size', 'Num of squares', 'Dimension']

    for k, v in dim.dim().items():
        tab.rows.append([f'1/{int(1 / k)}', dim[k], v])

    print(tab)


def at_end(*_):
    print_dim()
    sys.exit(0)


signal.signal(signal.SIGINT, at_end)


# region Pygame stuff
def init_pygame() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return screen, clock


def render(surface_: surface.Surface) -> None:
    p.draw(surface_)


def main_pygame() -> NoReturn:
    surface_, clock = init_pygame()
    up_num = 0

    while True:
        for _ in range(100):
            clock.tick(FPS)
            display.set_caption(f"Diffusion Limited Aggregation - {up_num}")
            up_num += 1
            for event in events.get():
                if event.type == pygame.QUIT:
                    at_end()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                at_end()

            p.update()

            surface_.fill(BLACK)

            render(surface_)

            display.flip()
        collect()
# endregion


def main_no_pygame() -> NoReturn:
    while True:
        for _ in range(100):
            p.update()
        collect()


def main() -> NoReturn:
    if USE_PYGAME:
        main_pygame()
    else:
        main_no_pygame()


if __name__ == '__main__':
    main()
