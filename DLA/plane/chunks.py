from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
from DLA import Vec2
from DLA.plane.chunk_view import _ChunkView

if TYPE_CHECKING:
    from .plane import Plane


class Chunks:
    """
    Chunk assignment
    ┌───────┬───────┐
    │       │       │
    │   0   │   1   │
    │       │       │
    ├───────┼───────┤
    │       │       │
    │   2   │   3   │
    │       │       │
    └───────┴───────┘
    """

    map = ((0, 1), (2, 3))
    map_T = ((0, 2), (1, 3))

    def __init__(self, start_pos: Vec2 | np.ndarray, size: float):
        x, y = start_pos
        self.size = size
        self.start_pos = np.array(start_pos)
        self.chunks: List[Optional[Plane]] = [None] * 4

    def __getitem__(self, idx: int) -> Optional[Plane]:
        return self.chunks[idx]

    def __setitem__(self, idx: int, val: Optional[Plane]) -> None:
        self.chunks[idx] = self.chunks[idx] or val

    def get_sub_coords(self, idx: int) -> Tuple[float, float]:
        halved_size = self.size / 2
        return (
            self.start_pos[0] + halved_size * (idx & 0b1),
            self.start_pos[1] + halved_size * ((idx & 0b10) >> 1),
        )

    def __iter__(self):
        return iter(self.chunks)

    def get_all_coords(self):
        return [self.get_sub_coords(i) for i in range(4)]

    def get_sub_chunks_for_point(
            self,
            point: Vec2 | np.ndarray
    ) -> Tuple[int, ...]:
        x, y = point - self.start_pos - (self.size / 2)
        x, y = int(x), int(y)

        if x == 0:
            if y == 0:
                return 0, 1, 2, 3
            return self.map[y > 0]
        elif y == 0:
            return self.map_T[x > 0]

        return (
            self.map[y > 0][x > 0],
        )

    def get_chunks(self, point: Vec2 | np.ndarray) -> _ChunkView:
        return _ChunkView(
            self.chunks,
            self.get_sub_chunks_for_point(point)
        )

    def __len__(self) -> int:
        return 4 - self.chunks.count(None)

    # def __bool__(self) -> bool:
    #     return len(self) > 0
