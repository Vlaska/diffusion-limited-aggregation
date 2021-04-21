#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np
cimport numpy as np
from cython.view cimport array as cvarray

ctypedef np.double_t DFLOAT
ctypedef np.npy_bool DBOOL


cpdef double[:] squared_distance(double[:, :] v):
    cdef Py_ssize_t i, size = v.shape[0]
    # cdef double[:] out = np.empty(size, dtype=np.double)
    cdef double[:] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="i")
    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return out


def does_collide(double[:, :] pos, double[:, :] point, float radius):
    #cdef double[:, :] diffs
    #cdef bool[:] t
    #cdef double[:] r
    cdef double[:, :] stuck_pos

    cdef Py_ssize_t pos_size = pos.shape[0]
    cdef Py_ssize_t i
    # for i in range(pos_size):
        
    #diffs = np.abs(pos - point)
    #t = squared_distance(diffs) < (4 * radius * radius)
    #r = diffs[t].compressed()
    #stuck_pos = r.reshape((r.shape[0] // 2, 2))

    #if stuck_pos.any():
    #    return True
    return False


def test_collisions(np.ndarray[DFLOAT, ndim=2] pos, np.ndarray[DFLOAT, ndim=2] points, float radius):
    cdef int i
    cdef np.ndarray v
    cdef list out = []
    for i, v in enumerate(points):
        if not v[0] is np.ma.masked and does_collide(pos, v, radius):
            out.append(v)
    return out
