from typing import List
import pytest
from pytest import MonkeyPatch
from DLA.plane import plane, base_plane
from DLA.plane import dimension


def test_add_point(monkeypatch: MonkeyPatch) -> None:
    from DLA.plane import plane, base_plane
    monkeypatch.setattr(plane, 'WINDOW_SIZE', 512)
    monkeypatch.setattr(plane, 'SECOND_MIN_BOX_SIZE', 32)
    monkeypatch.setattr(plane, 'STARTING_POS', (14, 16))
    monkeypatch.setattr(plane, 'NUM_OF_PARTICLES', 0)
    monkeypatch.setattr(base_plane, 'RADIUS', 1)

    p = plane.Plane.new()
    assert len(p) == 1  # type: ignore
    assert p[0]  # type: ignore
    assert len(p[0]) == 1  # type: ignore
    assert p[0][0]  # type: ignore
    assert len(p[0][0]) == 1  # type: ignore
    assert p[0][0][0]  # type: ignore
    assert len(p[0][0][0]) == 1  # type: ignore
    assert p[0][0][0][0]  # type: ignore
    assert len(
        p[0][0][0][0]  # type: ignore
    ) == 2
    assert p[0][0][0][0][0]  # type: ignore
    assert p[0][0][0][0][2]  # type: ignore


@pytest.mark.parametrize('points, results', [
    (0, [60, 224, 856, 3332, 13104, 51940]),
    (1, [120, 448, 1712, 6664, 26208, 103880]),
    (2, [180, 672, 2568, 9996, 39312, 155820]),
    (3, [196, 736, 2824, 11020, 43392, 172088]),
    (4, [234, 880, 3384, 13226, 52134, 206888]),
    (5, [238, 896, 3449, 13488, 53182, 211072]),
    (6, [285, 1070, 4106, 16023, 63207, 250949]),
    (7, [345, 1294, 4962, 19355, 76311, 302889]),
    (8, [371, 1390, 5332, 20805, 82045, 325693]),
])
def test_calc_dimension(
    monkeypatch: MonkeyPatch, points: int, results: List[int]
) -> None:
    from DLA.plane import particle_plane
    monkeypatch.setattr(plane, 'WINDOW_SIZE', 128)
    monkeypatch.setattr(plane, 'SECOND_MIN_BOX_SIZE', 1/32)
    monkeypatch.setattr(plane, 'NUM_OF_PARTICLES', 8)
    monkeypatch.setattr(plane, 'RADIUS', 2)
    monkeypatch.setattr(plane, 'STARTING_POS', (64, 64))
    monkeypatch.setattr(
        plane.NeighbouringPlanes,
        '_size_for_alt_plane_type',
        1 / 32)
    monkeypatch.setattr(base_plane, 'RADIUS', 2)
    monkeypatch.setattr(dimension, 'MIN_BOX_SIZE', 1/64)
    monkeypatch.setattr(dimension, 'SECOND_MIN_BOX_SIZE', 1/32)
    monkeypatch.setattr(
        particle_plane.SubPlaneParticlesAndIndivisible,
        '_size_for_alt_plane_type',
        1 / 32)

    p = plane.Plane.new()
    stuck_points = p._stuck_points.pos
    stuck_points[1:, :] = [
        [10, 10],  # 1
        [2, 2],  # 2
        [3, 2],  # 3
        [11, 12],  # 4
        [10, 11],  # 5
        [11.561, 14.56132],  # 6
        [16, 0],  # 7
        [17, 1],  # 8
    ]
    dimension.Dimension.init_lookup()

    for i in range(1, points + 1):
        p.add_point(i)

    dim = dimension.Dimension(p)
    dim.count()
    assert dim[1/2] == results[0]
    assert dim[1/4] == results[1]
    assert dim[1/8] == results[2]
    assert dim[1/16] == results[3]
    assert dim[1/32] == results[4]
    assert dim[1/64] == results[5]
