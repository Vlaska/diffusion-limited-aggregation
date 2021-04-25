from __future__ import annotations

from typing import Tuple, Union, cast

import numpy as np
from DLA import Vec
from numpy import ma

from .config import RADIUS


def random_in_range(
        a: float,
        b: float,
        shape: Union[Vec, Tuple[float, ...]]
) -> Vec:
    return (b - a) * np.random.random_sample(shape) + a


def squared_distance(v: np.ndarray) -> np.ndarray:
    return cast(np.ndarray, np.sum(v * v, axis=1))


def does_collide(pos: ma.MaskedArray, point: Vec) -> bool:
    diffs: np.ndarray = np.abs(pos - point)
    t = squared_distance(diffs) < (4 * RADIUS * RADIUS)
    r = diffs[t].compressed()
    stuck_pos = r.reshape((r.shape[0] // 2, 2))
    if len(stuck_pos):
        return True
    return False


def is_stuck(points, pos):
    out = []
    for i, v in enumerate(pos):
        if not v.mask.any() and does_collide(points, v):
            out.append(v)
    return out
