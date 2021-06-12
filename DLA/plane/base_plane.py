from __future__ import annotations

from typing import TYPE_CHECKING, Generator, List, Optional, Tuple, Union, cast, Type, Iterable

import numpy as np

from DLA import LIGHT_GRAY, Vec2
from DLA.config import RADIUS, USE_PYGAME
from DLA.utils import circle_in_subchunks, is_in_circle, one_subchunk_coords
from DLA.walker import StuckWalkers, WalkerPopulation

if USE_PYGAME or TYPE_CHECKING:
    import pygame
    from pygame import draw
    from pygame.surface import Surface


class BasePlane:
    _stuck_points: StuckWalkers
    _walking_points: WalkerPopulation
    _new_plane_type: Type[BasePlane]

    can_be_full: bool = True

    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = np.array(start, dtype=np.double)
        self.size = size
        self._init_pygame(start, size)
        self._sub_planes: List[Optional[BasePlane]] = [None] * 4
        self.full = False

    def set_full(self) -> None:
        pass

    def _add_point(self, point: int) -> Optional[List[int]]:
        if self.full:
            return None

        if self.can_be_full and is_in_circle(
                self.start_pos,
                self._stuck_points[point],
                self.size,
                RADIUS
        ):
            self.set_full()
            return None

        sub_chunks = circle_in_subchunks(
            self.start_pos, self._stuck_points[point], self.size, RADIUS
        )

        self.add_sub_chunks(sub_chunks)

        return sub_chunks

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            if not self._sub_planes[i]:
                self._sub_planes[i] = self._new_plane_type(
                    one_subchunk_coords(self.start_pos, self.size, i),
                    self.size / 2
                )

    def add_point(self, point: int) -> None:
        sub_planes = self._add_point(point)

        if sub_planes is None:
            return

        for i in sub_planes:
            cast(BasePlane, self._sub_planes[i]).add_point(point)

    # region Abstract Methods
    def are_full(self) -> bool:
        pass
    # endregion

    # region Magic Methods
    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 4 - self._sub_planes.count(None)

    def __getitem__(
        self, idx: Union[int, slice]
    ) -> Union[Optional[BasePlane], List[Optional[BasePlane]]]:
        return self._sub_planes[idx]

    def __setitem__(self, idx: int, val: Optional[BasePlane]) -> None:
        if not self._sub_planes[idx] and val:
            self._sub_planes[idx] = val

    def __iter__(self) -> Generator[BasePlane, None, None]:
        return (i for i in self._sub_planes if i)
    # endregion

    # region PyGame stuff
    if USE_PYGAME:  # noqa: C901
        def _init_pygame(self, start: Vec2, size: float) -> None:
            self.rect = pygame.Rect(
                *cast(Tuple[float, float], self.start_pos),
                self.size,
                self.size
            )

        def draw(self, surface: Surface) -> None:
            self._draw(surface)
            self._walking_points.draw(surface)
            self._stuck_points.draw(surface)

        def _draw(self, surface: Surface) -> None:
            if self.size <= 2:
                return
            draw.rect(surface, LIGHT_GRAY, self.rect, 1)
            if self.full:
                return
            for i in self._sub_planes:
                if i:
                    i._draw(surface)
    else:
        def _init_pygame(self, start: Vec2, size: float) -> None:
            pass

        def _draw(self, surface: Surface) -> None:
            pass

        def draw(self, surface: Surface) -> None:
            pass
    # endregion
