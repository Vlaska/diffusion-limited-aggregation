from __future__ import annotations

import signal
import sys
from gc import collect
from typing import Dict, TYPE_CHECKING, Final, NoReturn, Tuple, Union

from beautifultable import BeautifulTable
import numpy as np

from DLA import BLACK, config, plane, Vec
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
random_generator_state = np.random.get_state()
num_of_iterations = 0


def print_dim():
    dim = Dimension(p)
    dim.count()

    tab = BeautifulTable(precision=6)
    tab.columns.header = ['Box size', 'Num of squares', 'Dimension']

    for k, v in dim.dim().items():
        tab.rows.append([f'1/{int(1 / k)}', dim[k], v])

    print(tab)


def get_data() -> Dict[str, Union[Vec, float]]:
    out = {
        # 'starting_state': random_generator_state
        'radius': config['particle_radius'],
        'window_size': config['window_size'],
        'num_of_particles': config['num_of_particles'],
        'num_of_iterations': num_of_iterations,
    }
    out.update(p.get_data())
    dim = Dimension(p)
    dim.count()
    out.update(dim.get_data())
    return out


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
    global num_of_iterations

    while True:
        for _ in range(100):
            clock.tick(FPS)
            num_of_iterations += 1
            display.set_caption(
                f"Diffusion Limited Aggregation - {num_of_iterations}"
            )
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
    global num_of_iterations

    while True:
        for _ in range(100):
            num_of_iterations += 1
            p.update()
        collect()


def main() -> NoReturn:
    if USE_PYGAME:
        main_pygame()
    else:
        main_no_pygame()


if __name__ == '__main__':
    main()
