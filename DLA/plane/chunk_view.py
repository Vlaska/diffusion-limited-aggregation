from __future__ import annotations

from typing import List, Optional, Iterator, Tuple, Union
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plane import Plane


T = Union[List[int], Tuple[int, ...]]


class _ChunkView:
    def __init__(
            self,
            chunks: List[Optional[Plane]],
            selected: T
    ):
        self.chunks = chunks
        self.selected = selected

    def chunk_index(self, idx: int) -> int:
        return self.selected[idx]

    def __getitem__(self, idx: int) -> Optional[Plane]:
        return self.chunks[self.selected[idx]]

    def __setitem__(self, idx: int, val: Optional[Plane]):
        self.chunks[self.selected[idx]] = val

    def __iter__(self) -> Iterator[Optional[Plane]]:
        class _ChunkViewIterator(Iterator):
            chunks = self.chunks
            selected = self.selected

            def __init__(self) -> None:
                self.idx: int = 0

            def __next__(self) -> Optional[Plane]:
                if self.idx >= len(self.selected):
                    raise StopIteration

                out = self.chunks[self.selected[self.idx]]
                self.idx += 1

                return out

        return _ChunkViewIterator()
