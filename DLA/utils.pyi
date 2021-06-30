from __future__ import annotations

import array
from typing import List, Tuple

import numpy as np

from DLA.plane.base_plane import BasePlane

def one_sub_plane_coords(sub: np.ndarray, size: float,
                         idx: int) -> Tuple[float, float]: ...


def circle_in_sub_plane(sub_plane_coords: np.ndarray, circle_pos: np.ndarray,
                        size: float, radius: float) -> List[int]: ...


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


def check_particle_outside_plane(
    particle: np.ndarray,
    radius: float,
    plane_size: float
) -> array.array[int]: ...
