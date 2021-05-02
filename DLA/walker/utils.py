from __future__ import annotations

from typing import Tuple, Union

import numpy as np
from DLA import Vec
from DLA.utils import squared_distance

from .config import RADIUS


def random_in_range(
        a: float,
        b: float,
        shape: Union[Vec, Tuple[float, ...]]
) -> np.ndarray:
    return (b - a) * np.random.random_sample(shape) + a


def does_collide(pos: np.ndarray, point: Vec) -> bool:
    diffs: np.ndarray = np.abs(pos - point)
    t = squared_distance(diffs) < (4 * RADIUS * RADIUS)
    stuck_pos = diffs[t]
    if len(stuck_pos):
        return True
    return False


def is_stuck(points, pos):
    out = []
    for i, v in enumerate(pos):
        if not v[0] is np.NAN and does_collide(points, v):
            out.append(v)
    return out
