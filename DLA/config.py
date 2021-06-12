from __future__ import annotations

from typing import Final, Tuple

import numpy as np

try:
    from . import config_dict
except ImportError:
    # Used during testing
    config_dict = {
        'window_size': 512,
        'particle_radius': 3.0,
        'num_of_particles': 1000,
        'fps': 120,
        'min_box_size': 0.5,
        'start_pos': (256, 256),
        'epsilon': 1e-10,
        'push_out_tries': 10,
        'use_pygame': False,
        'print_results': False,
        'max_steps': 4000,
        'radius_check': 2,
        'regen_after_updates': 200,
        'step_strength': 2,
        'memory': 0
    }

FPS: Final[int] = config_dict['fps']
WINDOW_SIZE_FOR_RENDERING: Final[Tuple[int, int]] = (
    config_dict['window_size'], config_dict['window_size']
)
MIN_BOX_SIZE: Final[float] = config_dict['min_box_size']
USE_PYGAME: Final[bool] = config_dict['use_pygame']
RADIUS: Final[float] = config_dict['particle_radius']
SECOND_MIN_BOX_SIZE: Final[float] = \
    2 ** (np.log2(config_dict['min_box_size']) + 1)
WINDOW_SIZE: Final[int] = config_dict['window_size']
WINDOW_CENTER: Final[float] = WINDOW_SIZE // 2
EPSILON: Final[float] = config_dict['epsilon']
# + 1 to include radius of single particle
RADIUS_CHECK: Final[float] = (max(0, config_dict['radius_check']) + 1) * RADIUS
PUSH_OUT_TRIES: Final[int] = config_dict['push_out_tries']
REGENERATE_AFTER: Final[int] = config_dict['regen_after_updates']
ALPHA: Final[float] = config_dict['step_strength']
BETA: Final[float] = config_dict['memory']
NUM_OF_PARTICLES: Final[int] = config_dict['num_of_particles']
PRINT_RESULTS: Final[bool] = config_dict['print_results']
MAX_STEPS: Final[int] = config_dict['max_steps']
STARTING_POS: Final[Tuple[float, float]] = config_dict['start_pos']
PARTICLE_PLANE_SIZE: Final[float] = config_dict['particle_plane_size']
