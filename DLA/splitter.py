from __future__ import annotations

import sys
from typing import Final, Iterator, List, NoReturn, Optional, Tuple, cast

import numpy as np
import numpy.typing as npt
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as events
import pygame.key
import pygame.surface as surface
import pygame.time as time
import pygame.mouse as mouse

from loguru import logger

logger.add("logs/splitter - {time}.log", rotation="5MB",
           format="{time} | {level} | {message}")


Vec = npt.ArrayLike
Vec2 = Tuple[float, float]
RGB = Tuple[int, int, int]

WINDOW_WIDTH_AND_HEIGHT: Final[int] = 1024
RADIUS: Final[float] = 5.0
BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
PINK: Final[RGB] = (255, 0, 255)
RED: Final[RGB] = (255, 0, 0)
GREEN: Final[RGB] = (0, 255, 0)
FPS: Final[int] = 60
WINDOW_SIZE: Final[Tuple[int, int]] = (
    WINDOW_WIDTH_AND_HEIGHT, WINDOW_WIDTH_AND_HEIGHT
)
SCREEN_CENTER: Final[Vec2] = cast(
    Vec2, tuple(i / 2 for i in WINDOW_SIZE)
)
MIN_BOX_SIZE: Final[float] = 64


class ChunkMap:
    """[summary]

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
        halfed_size = self.size / 2
        return (
            self.start_pos[0] + halfed_size * (idx & 0b1),
            self.start_pos[1] + halfed_size * ((idx & 0b10) >> 1),
        )

    def __iter__(self):
        return iter(self.chunks)

    def get_all_coords(self):
        return [self.get_sub_coords(i) for i in range(4)]

    def get_subchunks_for_point(
        self,
        point: Vec2 | np.ndarray
    ) -> Tuple[int, ...]:
        x, y = point - self.start_pos - (self.size / 2)
        x, y = int(x), int(y)

        if x == 0:
            if y == 0:
                return (0, 1, 2, 3)
            return self.map[y > 0]
        elif y == 0:
            return self.map_T[x > 0]

        return (
            self.map[y > 0][x > 0],
        )

    class _ChunkView:
        def __init__(
            self,
            chunks: List[Optional[Plane]],
            selected: Tuple[int, ...]
        ):
            self.chunks = chunks
            self.selected = selected

        def chunk_index(self, idx: int) -> int:
            return self.selected[idx]

        def __getitem__(self, idx: int) -> Optional[Plane]:
            return self.chunks[self.selected[idx]]

        def __setitem__(self, idx: int, val: Optional[Plane]):
            self.chunks[self.selected[idx]] = val

        def __iter__(self) -> Iterator:
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

    def get_chunks(self, point: Vec2 | np.ndarray) -> ChunkMap._ChunkView:
        return self._ChunkView(
            self.chunks,
            self.get_subchunks_for_point(point)
        )

    def __len__(self) -> int:
        return 4 - self.chunks.count(None)

    # def __bool__(self) -> bool:
    #     return len(self) > 0


class Plane:
    def __init__(self, start: Vec2, size: float) -> None:
        self.start_pos = start
        self.size = size
        self.rect = pygame.Rect(*self.start_pos, self.size, self.size)
        # self.chunks: List[Plane] = []
        self.chunks = ChunkMap(start, size)

    @classmethod
    def new(cls) -> Plane:
        return cls((0, 0), WINDOW_WIDTH_AND_HEIGHT)

    def draw(self, surface: surface.Surface) -> None:
        draw.rect(surface, WHITE, self.rect, 1)
        for i in self.chunks:
            if i:
                i.draw(surface)

    def split(self) -> None:
        if self.chunks:
            # logger.debug("Split children")
            if self.size > MIN_BOX_SIZE:
                for i in self.chunks:
                    i.split()
        else:
            # logger.debug("Split self")
            halfed_size = self.size / 2
            for i, co in enumerate(self.chunks.get_all_coords()):
                self.chunks[i] = Plane(co, halfed_size)

    def split_at_point(self, point: Vec2 | np.ndarray) -> None:
        if self.size <= MIN_BOX_SIZE:
            return
        sub_chunks = self.chunks.get_chunks(point)
        logger.debug(f"Selected chunks: {tuple(sub_chunks.selected)}")
        for i, c in enumerate(sub_chunks):
            if not c:
                logger.debug(
                    "Created chunk at: "
                    f"{self.chunks.get_sub_coords(sub_chunks.chunk_index(i))} "
                    f"of size: {self.size / 2}"
                )
                sub_chunks[i] = c = Plane(
                    self.chunks.get_sub_coords(sub_chunks.chunk_index(i)),
                    self.size / 2
                )
            c.split_at_point(point)
            # add point ?


p = Plane.new()
points = np.empty((1000, 2), dtype=np.double)


def init() -> Tuple[surface.Surface, time.Clock]:
    pygame.init()
    clock = time.Clock()

    display.set_caption("Diffusion Limited Aggregation - Splitter")
    screen = display.set_mode(WINDOW_SIZE)

    display.flip()

    return (screen, clock)


def render(surface: surface.Surface, font: pygame.font.Font) -> None:
    p.draw(surface)

    mouse_pos = mouse.get_pos()
    text_surface = font.render(str(mouse_pos), True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (mouse_pos[0] + 15, mouse_pos[1] + 15)
    surface.blit(text_surface, text_rect)


def main() -> NoReturn:
    surface, clock = init()
    mouse_click_pos = None
    split_event = False
    font = pygame.font.SysFont('arial', 16)

    while True:
        clock.tick(FPS)

        for event in events.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    split_event = True
                elif event.key == pygame.K_r:
                    p.chunks = ChunkMap((0, 0), WINDOW_WIDTH_AND_HEIGHT)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_pos = event.pos
                logger.debug(f"Clicked at: {mouse_click_pos}")
                p.split_at_point(mouse_click_pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_click_pos = None

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            sys.exit(0)

        if split_event:
            p.split()
            split_event = False
        # if mouse.get_pressed(pygame.)

        surface.fill(BLACK)

        render(surface, font)

        if mouse_click_pos:
            # print(mouse_click_pos)
            mouse_click_pos = mouse.get_pos() or mouse_click_pos
            draw.circle(surface, GREEN, mouse_click_pos, 1)

        display.flip()


if __name__ == '__main__':
    main()
