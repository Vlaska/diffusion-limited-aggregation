from __future__ import annotations

from typing import List, Tuple

import numpy as np

from DLA.plane.base_plane import BasePlane

def one_subchunk_coords(start: np.ndarray, size: float,
                        idx: int) -> Tuple[float, float]: ...


def circle_in_subchunks(start: np.ndarray, circle_pos: np.ndarray,
                        size: float, raduis: float) -> List[int]: ...


def dot_self(a: np.ndarray) -> float: ...


def is_in_circle(
    pos: np.ndarray,
    c_pos: np.ndarray,
    size: float,
    radius: float
) -> bool: ...


def get_collision_time(
    plane: BasePlane,
    particle_plane_size: float,
    moving_part: np.ndarray,
    move_vec: np.ndarray,
    radius: float
) -> float: ...
