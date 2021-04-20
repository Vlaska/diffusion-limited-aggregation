#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np
cimport numpy as np

ctypedef np.double_t DFLOAT
ctypedef np.npy_bool DBOOL


def squared_distance(np.ndarray[DFLOAT, ndim=2] v):
    return np.sum(v * v, axis=1)


def does_collide(np.ndarray[DFLOAT, ndim=2] pos, np.ndarray[DFLOAT, ndim=1] point, float radius):
    cdef np.ndarray[DFLOAT, ndim=2] diffs
    cdef np.ndarray[DBOOL, ndim=1] t
    cdef np.ndarray[DFLOAT, ndim=1] r
    cdef np.ndarray[DFLOAT, ndim=2] stuck_pos

    diffs = np.abs(pos - point)
    t = squared_distance(diffs) < (4 * radius * radius)
    r = diffs[t].compressed()
    stuck_pos = r.reshape((r.shape[0] // 2, 2))

    if stuck_pos.any():
        return True
    return False


def test_collisions(np.ndarray[DFLOAT, ndim=2] pos, np.ndarray[DFLOAT, ndim=2] points, float radius):
    cdef int i
    cdef np.ndarray v
    cdef list out = []
    for i, v in enumerate(points):
        if not v[0] is np.ma.masked and does_collide(pos, v, radius):
            out.append(v)
    return out
