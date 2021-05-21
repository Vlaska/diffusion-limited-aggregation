import numpy as np
import pytest
from pytest import MonkeyPatch
from DLA import config
from DLA.plane.plane import Plane

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


def test_add_point(monkeypatch: MonkeyPatch) -> None:
    from DLA.plane import base_plane
    from DLA.plane import plane
    monkeypatch.setattr(plane, 'WINDOW_WIDTH_AND_HEIGHT', 512)
    monkeypatch.setattr(plane, 'SECOND_MIN_BOX_SIZE', 32)
    monkeypatch.setattr(base_plane, 'RADIUS', 1)
    monkeypatch.setitem(config, 'start_pos', (14, 16))
    monkeypatch.setitem(config, 'num_of_particles', 0)
    p = Plane.new()
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
