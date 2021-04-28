#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np
cimport numpy as np
from cython.view cimport array as cvarray

ctypedef np.double_t DFLOAT
ctypedef np.npy_bool DBOOL


cpdef np.ndarray[double, ndim=1] squared_distance(double[:, :] v):
    cdef Py_ssize_t i, size = v.shape[0]
    # cdef double[:] out = np.empty(size, dtype=np.double)
    cdef double[:] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="d")
    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return np.asarray(out)


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


cpdef bint in_square(double[:] a, double[:] b, double[:] point):
    return a[0] <= point[0] and point[0] <= b[0] and a[1] <= point[1] and point[1] <= b[1]


# cdef bint circle_square_collision((double, double) s_pos, double[:] c_pos, double s_size, double radius):
cdef bint circle_square_collision((double, double) s_pos, double[:] c_pos, double s_size, double radius):
    cdef double tX = c_pos[0], tY = c_pos[1]
    cdef double dX, dY

    if c_pos[0] < s_pos[0]:
        tX = s_pos[0]
    elif c_pos[0] > s_pos[0] + s_size:
        tX = s_pos[0] + s_size

    if c_pos[1] < s_pos[1]:
        tY = s_pos[1]
    elif c_pos[1] > s_pos[1] + s_size:
        tY = s_pos[1] + s_size

    dX = c_pos[0] - tX
    dY = c_pos[1] - tY

    return (dX * dX) + (dY * dY) < radius * radius


#cdef iter_chunks(double x, double y, double size):
#    for i in range(4):
#        yield (
#            x + size * (i & 0b1),
#            y + size * ((i & 0b10) >> 1),
#        )
#
#
#cpdef bint circle_in_subchunks((double, double) start, double[:] circle_pos, double size, double radius):
#    cdef double x = start[0], y = start[1]
    
