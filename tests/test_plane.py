import numpy as np
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


def test_calc_dimension(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(plane, 'WINDOW_SIZE', 128)
    monkeypatch.setattr(plane, 'SECOND_MIN_BOX_SIZE', 1/4)
    monkeypatch.setattr(plane, 'NUM_OF_PARTICLES', 5)
    monkeypatch.setattr(plane, 'STARTING_POS', (64, 64))
    monkeypatch.setattr(base_plane, 'RADIUS', 2)
    monkeypatch.setattr(dimension, 'MIN_BOX_SIZE', 1/8)

    p = plane.Plane.new()
    stuck_points = p._stuck_points.pos
    stuck_points[1:, :] = [
        [10, 10],
        [2, 0],
        [3, 1],
        [11, 12],
        [10, 11]
    ]
    dimension.Dimension.init_lookup()
    dim = dimension.Dimension(p)
    dim.count()
    assert dim[1/2] == 60
