from typing import Iterable, List, Optional, TYPE_CHECKING


from DLA import LIGHT_GRAY
from DLA.plane.base_plane import USE_PYGAME, BasePlane

if USE_PYGAME or TYPE_CHECKING:
    from pygame import draw
    from pygame.surface import Surface


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
