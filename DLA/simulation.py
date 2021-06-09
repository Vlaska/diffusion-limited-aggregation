from __future__ import annotations

import pickle
import signal
import sys
from datetime import datetime
from gc import collect
from pathlib import Path
from typing import TYPE_CHECKING, Dict, NoReturn, Tuple, Union

import numpy as np
from beautifultable import BeautifulTable

from DLA import BLACK, Vec, plane
from DLA.config import (ALPHA, BETA, FPS, MAX_STEPS, NUM_OF_PARTICLES,
                        PRINT_RESULTS, RADIUS, USE_PYGAME, WINDOW_SIZE,
                        WINDOW_SIZE_FOR_RENDERING)
from DLA.exceptions import StopSimulation
from DLA.plane.dimension import Dimension

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
    out: Dict[str, Union[float, np.ndarray]] = {
        # 'starting_state': random_generator_state
        'radius': RADIUS,
        'window_size': WINDOW_SIZE,
        'num_of_particles': NUM_OF_PARTICLES,
        'memory': BETA,
        'step_strength': ALPHA,
        'num_of_iterations': num_of_iterations,
    }

    out.update(p.get_data())
    dim = Dimension(p)
    dim.count()
    out.update(dim.get_data())
    return out


def save_data():
    data = get_data()
    raw_data = pickle.dumps(data)
    filename = f'{datetime.now().strftime("%d.%m.%Y-%H.%M.%S.%f")}.pickle'
    Path(filename).write_bytes(raw_data)
    print(filename)


def at_end(*_):
    if PRINT_RESULTS:
        print_dim()
    save_data()
    sys.exit(0)


signal.signal(signal.SIGINT, at_end)


# region Pygame stuff
def init_pygame() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation")
    screen = display.set_mode(WINDOW_SIZE_FOR_RENDERING)

    display.flip()

    return screen, clock


def render(surface_: surface.Surface) -> None:
    p.draw(surface_)


def main_pygame() -> NoReturn:
    surface_, clock = init_pygame()
    global num_of_iterations

    for _ in range(MAX_STEPS // 100):
        try:
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

                surface_.fill((0, 0, 0, 60))

                render(surface_)

                display.flip()
            collect()
        except StopSimulation:
            while True:
                clock.tick(FPS)

                for event in events.get():
                    if event.type == pygame.QUIT:
                        at_end()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    at_end()

                surface_.fill(BLACK)

                render(surface_)

                display.flip()
# endregion


def main_no_pygame() -> NoReturn:
    global num_of_iterations
    try:
        for _ in range(MAX_STEPS // 100):
            for _ in range(100):
                num_of_iterations += 1
                p.update()
            collect()
    except StopSimulation:
        pass
    finally:
        at_end()


def main() -> NoReturn:
    if USE_PYGAME:
        main_pygame()
    else:
        main_no_pygame()


if __name__ == '__main__':
    main()
