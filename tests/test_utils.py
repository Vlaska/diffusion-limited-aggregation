from DLA.utils import one_subchunk_coords
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
