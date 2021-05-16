from __future__ import annotations

from typing import Dict, TYPE_CHECKING, Final, Generator, List, Optional, Tuple, Type, TypeVar, cast

import numpy as np

from DLA import LIGHT_GRAY, Vec2, config
from DLA.utils import circle_in_subchunks, is_in_circle
from DLA.walker import StuckWalkers, WalkerPopulation

SECOND_MIN_BOX_SIZE: Final[float] = config['second_min_box_size']
RADIUS: Final[float] = config['particle_radius']
USE_PYGAME: Final[bool] = config['use_pygame']

if USE_PYGAME or TYPE_CHECKING:
    import pygame
    from pygame import draw
    from pygame.surface import Surface


K = TypeVar('K')
V = TypeVar('V')


class _ObjectPool(Dict[K, List[V]]):
    def __getitem__(self, k: K) -> List[V]:
        try:
            return super().__getitem__(k)
        except KeyError:
            t: List[V] = []
            self[k] = t
            return t


class PlaneFactory(type):
    def __call__(cls, start: Vec2, size: float) -> BasePlane:  # type: ignore
        pool = cls._object_pool[cls]  # type: ignore
        obj: BasePlane

        if pool:
            print("Got from pool")
            obj = pool.pop()
            obj._init(start, size)
        else:
            # print("New object")
            obj = super(PlaneFactory, cls).__call__(start=start, size=size)

        return obj


class BasePlane(metaclass=PlaneFactory):
    _stuck_points: StuckWalkers
    _walking_points: WalkerPopulation
    _object_pool: _ObjectPool[Type[BasePlane], BasePlane] = _ObjectPool()

    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = np.empty(2, dtype=np.double)
        self._init(start, size)

    @property
    def size(self) -> float:
        return self._size

    @size.setter
    def size(self, size: float) -> None:
        self._size = size

    # def __new__(cls, start: Vec2, size: float) -> BasePlane:
    #     pool = cls._object_pool[cls]
    #     obj: BasePlane

    #     if pool:
    #         print("Got from pool")
    #         obj = pool.pop()
    #         obj._init(start, size)
    #     else:
    #         # print("New object")
    #         obj = super().__new__(cls)

    #     return obj

    def _init(self, start: Vec2, size: float) -> None:
        self.start_pos[:] = start
        self.size = size
        self._init_pygame(start, size)
        self._sub_planes: List[Optional[BasePlane]] = [None] * 4
        self.full = False

    def set_full(self) -> None:
        self.full = True

    def _add_point(self, point: int) -> Optional[List[int]]:
        if self.full:
            return None

        if is_in_circle(
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

    def _reset(self) -> None:
        for i in self._sub_planes:
            if isinstance(i, BasePlane):
                i._reset()
        self._object_pool[self.__class__].append(self)
        print("Returned to pool")

    # region Abstract
    def add_sub_chunks(self, chunks) -> None:
        pass

    def are_full(self) -> bool:
        pass

    def add_point(self, point: int) -> None:
        pass
    # endregion

    # region Magic Methods
    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 4 - self._sub_planes.count(None)

    def __getitem__(self, idx: int) -> Optional[BasePlane]:
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
