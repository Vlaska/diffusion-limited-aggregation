from __future__ import annotations

from functools import cached_property
from typing import (TYPE_CHECKING, Final, Generator, Iterable, List, Optional,
                    Tuple, Type, cast, no_type_check)

import numpy as np
from DLA import LIGHT_GRAY, Vec2, config
from DLA.utils import circle_in_subchunks, is_in_circle, one_subchunk_coords
from DLA.walker import StuckWalkers, WalkerPopulation

WINDOW_WIDTH_AND_HEIGHT: Final[int] = config['window_size']
MIN_BOX_SIZE: Final[float] = config['min_box_size']
SECOND_MIN_BOX_SIZE: Final[float] = config['second_min_box_size']
RADIUS: Final[float] = config['particle_radius']
USE_PYGAME: Final[bool] = config['use_pygame']

if USE_PYGAME or TYPE_CHECKING:
    import pygame
    from pygame import draw
    from pygame.surface import Surface


class Plane:
    """
    Sub planes assignment
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

    _stuck_points: StuckWalkers
    _walking_points: WalkerPopulation

    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = np.array(start, dtype=np.double)
        self.size = size
        self._init_pygame(start, size)
        self._sub_planes: List[Optional[Plane]] = [None] * 4
        self.full = False
        self._new_plane_creator: Type[Plane] = (
            self._indivisible_plane
            if SECOND_MIN_BOX_SIZE == self.size / 2 else Plane
        )

    def __new__(cls, start: Vec2, size: float) -> Plane:
        return super().__new__(cls)

    @cached_property
    def _indivisible_plane(self) -> Type[Plane]:
        from DLA.plane.indivisible_plane import IndivisiblePlane
        return IndivisiblePlane

    def update(self):
        self._walking_points.update(self._stuck_points)

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            if not self._sub_planes[i]:
                self._sub_planes[i] = self._new_plane_creator(
                    one_subchunk_coords(self.start_pos, self.size, i),
                    self.size / 2
                )

    def set_full(self) -> None:
        self.full = True
        del self._sub_planes

    def _add_point(self, point: int) -> Tuple[bool, Optional[List[int]]]:
        if self.full:
            return True, None

        if is_in_circle(
            self.start_pos,
            self._stuck_points[point],
            self.size,
            RADIUS
        ):
            self.set_full()
            return True, None

        sub_chunks = circle_in_subchunks(
            self.start_pos, self._stuck_points[point], self.size, RADIUS
        )

        self.add_sub_chunks(sub_chunks)

        return False, sub_chunks

    def add_point(self, point: int) -> None:
        done, sub_chunks = self._add_point(point)

        if done:
            return

        for i in cast(List[int], sub_chunks):
            cast(Plane, self._sub_planes[i]).add_point(point)

        if self.are_full():
            self.set_full()

        return

    @staticmethod
    def _check_is_full(v: Optional[Plane]) -> bool:
        return v and v.full  # type: ignore

    @no_type_check
    def are_full(self) -> bool:
        return self.full or all(
            self._check_is_full(self._sub_planes[i]) for i in range(4)
        )

    @classmethod
    def new(cls) -> Plane:
        obj = cls((0, 0), WINDOW_WIDTH_AND_HEIGHT)

        cls._walking_points = WalkerPopulation(config['num_of_particles'])
        cls._stuck_points = StuckWalkers(
            cls._walking_points, config['start_pos'], obj
        )

        # * Method called at initialization of simulation;
        # * There is only one point present
        obj.add_point(0)

        return obj

    # region Magic Methods
    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 4 - self._sub_planes.count(None)

    def __getitem__(self, idx: int) -> Optional[Plane]:
        return self._sub_planes[idx]

    def __setitem__(self, idx: int, val: Optional[Plane]) -> None:
        if not self._sub_planes[idx] and val:
            self._sub_planes[idx] = val

    def __iter__(self) -> Generator[Plane, None, None]:
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
        def _init_pygame(self, start: Vec2, size: float) -> None: ...
        def draw(self, surface: Surface) -> None: ...
        def _draw(self, surface: Surface) -> None: ...
    # endregion
