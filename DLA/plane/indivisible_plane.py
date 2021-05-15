from typing import List, Optional, Iterable

from pygame import draw
from pygame.surface import Surface

from DLA import LIGHT_GRAY
from DLA.plane import Plane


class IndivisiblePlane(Plane):
    _sub_planes: List[Optional[bool]]  # type: ignore

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            self._sub_planes[i] = True

    def add_point(self, point: int) -> None:
        done, _ = self._add_point(point)

        if done:
            return

        if len(self) == 4:
            self.set_full()

        return

    def _draw(self, surface: Surface) -> None:
        draw.rect(surface, LIGHT_GRAY, self.rect, 1)

    def are_full(self) -> bool:
        return self.full
