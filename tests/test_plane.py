import numpy as np
import pytest
from DLA.splitter import ChunkMap, Plane


POINTS_TO_TEST = [
    [(0, 0), (0, )],
    [(1, 1), (0, )],
    [(17, 0), (1, )],
    [(0, 17), (2, )],
    [(17, 17), (3, )],
    [(16, 16), (0, 1, 2, 3)],
    [(16, 0), (0, 1)],
    [(16, 17), (2, 3)],
    [(0, 16), (0, 2)],
    [(17, 16), (1, 3)],
]
offset = np.array((15, 15))


@pytest.mark.parametrize('coord,result', POINTS_TO_TEST)
def test_get_chunk_for_point(coord, result):
    chunk_map = ChunkMap((0, 0), 32)
    assert chunk_map.get_subchunks_for_point(coord) == result


@pytest.mark.parametrize('coord,result', POINTS_TO_TEST)
def test_get_chunk_for_point_with_offset(coord, result):
    chunk_map_offset = ChunkMap(offset, 32)
    assert chunk_map_offset.get_subchunks_for_point(coord + offset) == result


def test_ChunkMap_len():
    chunk_map = ChunkMap(offset, 32)
    assert len(chunk_map) == 0
    chunk_map.chunks[0] = ""
    assert len(chunk_map) == 1


def test_ChunkMap_view():
    pass


def test_ChunkMap_iteration():
    chunk_map = ChunkMap((0, 0), 32)
    for i in range(4):
        chunk_map.chunks[i] = i + 10

    assert list(chunk_map.get_chunks((0, 0))) == [10]
    assert list(chunk_map.get_chunks((17, 17))) == [13]
    assert list(chunk_map.get_chunks((16, 15))) == [10, 11]
    assert list(chunk_map.get_chunks((15, 16))) == [10, 12]
    assert list(chunk_map.get_chunks((16, 16))) == [10, 11, 12, 13]


def test_ChunkMap_coords():
    chunk_map = ChunkMap(offset, 32)
    assert chunk_map.get_sub_coords(0) == tuple(offset)
    assert chunk_map.get_sub_coords(1) == (offset[0] + 16, offset[1])
    assert chunk_map.get_sub_coords(2) == (offset[0], offset[1] + 16)
    assert chunk_map.get_sub_coords(3) == (offset[0] + 16, offset[1] + 16)


def test_spliting_at_point():
    p = Plane((0, 0), 1024)
    split_point = (227, 163)
    p.split_at_point(split_point)
    assert p.chunks[0]
    assert p.chunks[0].chunks[0]
    assert p.chunks[0].chunks[0].chunks[3]
    assert p.chunks[0].chunks[0].chunks[3].chunks[1]
    assert len(p.chunks[0].chunks[0].chunks[3].chunks[1].chunks) == 0