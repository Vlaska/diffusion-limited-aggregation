import numpy as np
import pytest
from DLA.splitter import ChunkMap


POINTS_TO_TEST = [
    [(0, 0), (0, )],
    [(1, 1), (0, )],
    [(33, 0), (1, )],
    [(0, 33), (2, )],
    [(33, 33), (3, )],
    [(32, 32), (0, 1, 2, 3)],
    [(32, 0), (0, 1)],
    [(32, 33), (2, 3)],
    [(0, 32), (0, 2)],
    [(33, 32), (1, 3)],
]
offset = np.array((15, 15))


@pytest.mark.parametrize('coord,result', POINTS_TO_TEST)
def test_get_chunk_for_point(coord, result):
    chunk_map = ChunkMap((0, 0), 32)
    assert chunk_map.get_chunks_for_point(coord) == result


@pytest.mark.parametrize('coord,result', POINTS_TO_TEST)
def test_get_chunk_for_point_with_offset(coord, result):
    chunk_map_offset = ChunkMap(offset, 32)
    assert chunk_map_offset.get_chunks_for_point(coord + offset) == result


def test_ChunkMap_len():
    chunk_map = ChunkMap(offset, 32)
    assert len(chunk_map) == 0
    chunk_map.chunks[0] = ""
    assert len(chunk_map) == 1


def test_ChunkMap_view():
    pass


def test_ChunkMap_iteration():
    chunk_map = ChunkMap(offset, 32)
    for i in range(4):
        chunk_map.chunks[i] = i + 10

    assert list(chunk_map.get_chunks((16, 16))) == [10]
    assert list(chunk_map.get_chunks((48, 48))) == [13]
    assert list(chunk_map.get_chunks((47, 16))) == [10, 11]
    assert list(chunk_map.get_chunks((16, 47))) == [10, 12]
    assert list(chunk_map.get_chunks((47, 47))) == [10, 11, 12, 13]


def test_ChunkMap_coords():
    chunk_map = ChunkMap(offset, 32)
    assert chunk_map.coords(0) == tuple(offset)
    assert chunk_map.coords(1) == (offset[0] + 32, offset[1])
    assert chunk_map.coords(2) == (offset[0], offset[1] + 32)
    assert chunk_map.coords(3) == (offset[0] + 32, offset[1] + 32)
