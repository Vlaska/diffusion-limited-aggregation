from __future__ import annotations

from typing import Tuple, Final

from . import config


FPS: Final[int] = 60
WINDOW_SIZE_FOR_RENDERING: Final[Tuple[int, int]] = (
    config['window_size'], config['window_size']
)
MIN_BOX_SIZE: Final[float] = 64
USE_PYGAME: Final[bool] = config['use_pygame']
RADIUS: Final[float] = config['particle_radius']
SECOND_MIN_BOX_SIZE: Final[float] = config['second_min_box_size']
WINDOW_SIZE: Final[int] = config['window_size']
WINDOW_CENTER: Final[float] = WINDOW_SIZE // 2
SQUARED_PARTICLE_DISTANCE: Final[float] = 4 * RADIUS * RADIUS
EPSILON: Final[float] = config['epsilon']
RADIUS_CHECK: Final[float] = (max(0, config['radius_check']) + 1) * RADIUS
PUSH_OUT_TRIES: Final[int] = config['push_out_tries']
BORDER_U_L: Final[float] = RADIUS
BORDER_D_R: Final[float] = config['window_size'] - RADIUS
REGENERATE_AFTER: Final[int] = config['regen_after_updates']
ALPHA: Final[float] = config['step_strength']
BETA: Final[float] = config['memory']