from __future__ import annotations

from typing import Final, Tuple

import numpy as np

from . import config_dict

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
