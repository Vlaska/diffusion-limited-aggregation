from DLA.utils import one_subchunk_coords, subchunk_coords
import pytest
import numpy as np


@pytest.mark.parametrize('idx, result', [
    [0, (0.0, 0.0)],
    [1, (256.0, 0.0)],
    [2, (0.0, 256.0)],
    [3, (256.0, 256.0)],
])
def test_one_subchunk_coords(idx, result):
    assert one_subchunk_coords(
        np.array((0, 0), dtype=np.double), 512, idx) == result


@pytest.mark.parametrize('coords, size, results', [
    [(0.0, 0.0), 256, [(0, 0), (128, 0), (0, 128), (128, 128)]],
    [
        (47.5, 13.3345), 512, [
            (47.5, 13.3345), (303.5, 13.3345),
            (47.5, 269.3345), (303.5, 269.3345),
        ]
    ],
])
def test_subchunk_coords(coords, size, results):
    assert subchunk_coords(np.array(coords, dtype=np.double), size) == results
