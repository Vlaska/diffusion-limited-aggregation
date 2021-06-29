from __future__ import annotations

from typing import Final, Tuple

import numpy as np

try:
    from . import config_dict
except ImportError:
    # Used during testing
    config_dict = {
        'display': {
            'fps': 120,
            'window_size': 512,
            'use_pygame': False,
            'print_results': False,
        },

        'particles': {
            'radius': 3.0,
            'num': 1000,
            'start_pos': (256, 256),
        },

        'system': {
            'push_out_tries': 10,
            'max_steps': 4000,
            'regen_after_updates': 200,
        },

        'planes': {
            'min_box_size': 0.5,
            'particle_collision_plane_size': 32,
        },

        'simulation': {
            'step_strength': 2,
            'memory': 0,
        },
    }

FPS: Final[int] = config_dict['display']['fps']
WINDOW_SIZE: Final[int] = config_dict['display']['window_size']
USE_PYGAME: Final[bool] = config_dict['display']['use_pygame']
PRINT_RESULTS: Final[bool] = config_dict['display']['print_results']
WINDOW_SIZE_FOR_RENDERING: Final[Tuple[int, int]] = (WINDOW_SIZE, WINDOW_SIZE)

RADIUS: Final[float] = config_dict['particles']['radius']
NUM_OF_PARTICLES: Final[int] = config_dict['particles']['num']
STARTING_POS: Final[Tuple[float, float]] = \
    config_dict['particles']['start_pos']

PUSH_OUT_TRIES: Final[int] = config_dict['system']['push_out_tries']
MAX_STEPS: Final[int] = config_dict['system']['max_steps']
REGENERATE_AFTER: Final[int] = config_dict['system']['regen_after_updates']

MIN_BOX_SIZE: Final[float] = config_dict['planes']['min_box_size']
PARTICLE_PLANE_SIZE: Final[float] = \
    config_dict['planes']['particle_collision_plane_size']
SECOND_MIN_BOX_SIZE: Final[float] = 2 ** (np.log2(MIN_BOX_SIZE) + 1)

ALPHA: Final[float] = config_dict['simulation']['step_strength']
BETA: Final[float] = config_dict['simulation']['memory']
