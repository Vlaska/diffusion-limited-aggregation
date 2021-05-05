from __future__ import annotations

from typing import Final, OrderedDict, TYPE_CHECKING

import numpy as np
from DLA import config

if TYPE_CHECKING:
    from .plane import Plane

_KT = float
_VT = float
MIN_BOX_SIZE: Final[float] = config['min_box_size']


class Dimension(OrderedDict[_KT, _VT]):
    def __init__(self, plane: Plane) -> None:
        self.plane = plane

    def count(self):
        self._count(self.plane)

    def _count(self, plane: Plane):
        if plane.size <= MIN_BOX_SIZE:
            return
        self[plane.size / 2] += len(plane)
        for i in plane:
            if i:
                self._count(i)

    def dim(self) -> OrderedDict[_KT, _VT]:
        out = OrderedDict()

        for k, v in self.items():
            if k < 1:
                out[k] = np.log(v) / np.log(1 / k)

        return out

    def __getitem__(self, k: _KT) -> _VT:
        try:
            return super().__getitem__(k)
        except KeyError:
            return 0
