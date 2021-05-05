from __future__ import annotations

from typing import Tuple, Union

import numpy as np
from DLA import Vec


def random_in_range(
        a: float,
        b: float,
        shape: Union[Vec, Tuple[float, ...]]
) -> np.ndarray:
    return (b - a) * np.random.random_sample(shape) + a
