from __future__ import annotations

from typing import List, Tuple

import numpy as np


def squared_distance(v: np.ndarray) -> np.ndarray: ...


# def does_collide(pos: np.ndarray, point: np.ndarray,
#                  radius: float) -> bool: ...


# def test_collisions(pos: np.ndarray, point: np.ndarray,
#                     radius: float) -> List[bool]: ...


def one_subchunk_coords(start: np.ndarray, size: float,
                        idx: int) -> Tuple[float, float]: ...


def subchunk_coords(start: np.ndarray,
                    size: float) -> List[Tuple[float, float]]: ...


def circle_in_subchunks(start: np.ndarray, circle_pos: np.ndarray,
                        size: float, raduis: float) -> List[int]: ...


def correct_circle_pos(
    new_pos: np.ndarray,
    step: np.ndarray,
    stuck_point: np.ndarray,
    radius: float
) -> np.ndarray: ...
