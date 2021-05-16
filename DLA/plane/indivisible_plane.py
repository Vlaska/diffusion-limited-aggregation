from typing import Iterable, List, Optional

from pygame import draw
from pygame.surface import Surface
from loguru import logger

from DLA import LIGHT_GRAY
from DLA.plane.base_plane import USE_PYGAME, BasePlane


class IndivisiblePlane(BasePlane):
    _sub_planes: List[Optional[bool]]  # type: ignore

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            self._sub_planes[i] = True

    def add_point(self, point: int) -> None:
        sub_planes = self._add_point(point)

        if sub_planes is None:
            return

        if len(self) == 4:
            self.set_full()

        return

    if USE_PYGAME:
        def _draw(self, surface: Surface) -> None:
            draw.rect(surface, LIGHT_GRAY, self.rect, 1)

    def are_full(self) -> bool:
        return self.full

    def _reset(self) -> None:
        self._object_pool[self.__class__].add(self)
        logger.debug(f"Added to pool: {self.__class__.__name__}, {id(self)}")
        self._sub_planes = [None] * 4
        # print("Returned to pool")
