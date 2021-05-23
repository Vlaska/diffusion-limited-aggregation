from __future__ import annotations

from typing import TYPE_CHECKING, Dict, OrderedDict

import numpy as np

from DLA import Vec
from DLA.config import MIN_BOX_SIZE, SECOND_MIN_BOX_SIZE, WINDOW_SIZE

if TYPE_CHECKING:
    from .base_plane import BasePlane
    from .plane import Plane

_KT = float
_VT = float


class Dimension(OrderedDict[_KT, _VT]):
    lookup_tab: Dict[float, Dict[float, int]]

    @classmethod
    def init_lookup(cls):
        cls.lookup_tab = {
            2 ** i: {}
            for i in range(
                int(np.log2(MIN_BOX_SIZE)) + 1, int(np.log2(WINDOW_SIZE)) + 1
            )
        }
        o = int(np.log2(MIN_BOX_SIZE)) - 1
        for k, v in cls.lookup_tab.items():
            u = 4
            for j in range(int(np.log2(k)) - 1, o, -1):
                v[2 ** j] = u
                u *= 4

    def __init__(self, plane: Plane) -> None:
        self.plane = plane

    def count(self):
        self._count(self.plane)

    def _count(self, plane: BasePlane):

        if plane.full:
            self._count_full(plane.size)
            return

        self[plane.size / 2] += len(plane)

        if plane.size == SECOND_MIN_BOX_SIZE:
            return

        for i in plane:
            if i:
                self._count(i)

    def _count_full(self, size: float):
        for k, v in self.lookup_tab[size].items():
            self[k] += v

    def dim(self) -> OrderedDict[_KT, _VT]:
        out = OrderedDict()

        for k, v in self.items():
            if k < 1:
                out[k] = np.log(v) / np.log(1 / k)

        return out

    def get_data(self) -> Dict[str, Vec]:
        return {
            'box_size': np.array(list(self.keys())),
            'num_of_boxes': np.array(list(self.values())),
            'dimension': np.array(list(self.dim().values())),
        }

    def __getitem__(self, k: _KT) -> _VT:
        try:
            return super().__getitem__(k)
        except KeyError:
            return 0


Dimension.init_lookup()
