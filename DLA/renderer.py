from __future__ import annotations

import pickle
import sys
from pathlib import Path

from DLA.particles import StuckParticles, WalkingParticles
from DLA.simulation import init_pygame

try:
    import pygame
    import pygame.display as display
    import pygame.event as events
except ImportError:
    print("PyGame is required, to render DLA.")
    sys.exit(1)


def render(pickle_file: Path, only_stuck: bool = False) -> None:
    sim_data = pickle.loads(pickle_file.read_bytes())
    window_size: int = sim_data['window_size']
    surface, clock = init_pygame((window_size, window_size))

    walking_particles = WalkingParticles.load_for_render(
        sim_data['free_particles']
    )
    stuck_particles = StuckParticles.load_for_render(
        walking_particles,
        sim_data['stuck_particles']
    )

    while True:
        clock.tick(60)

        surface.fill((255, 255, 255))

        for event in events.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            sys.exit(0)

        stuck_particles.draw(surface)
        if not only_stuck:
            walking_particles.draw(surface)

        display.flip()
