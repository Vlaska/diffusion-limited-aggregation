#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np
cimport numpy as np
cimport cython
from cython.view cimport array as cvarray

ctypedef np.double_t DFLOAT
ctypedef np.npy_bool DBOOL

ctypedef fused number:
    int
    long
    double


cpdef np.ndarray[double, ndim=1] squared_distance(double[:, :] v):
    cdef Py_ssize_t i, size = v.shape[0]
    # cdef double[:] out = np.empty(size, dtype=np.double)
    cdef double[:] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="d")
    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return np.asarray(out)


def does_collide(double[:, :] pos, double[:, :] point, number radius):
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


def test_collisions(np.ndarray[DFLOAT, ndim=2] pos, np.ndarray[DFLOAT, ndim=2] points, number radius):
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
cdef bint circle_square_collision(number s_x, number s_y, double[:] c_pos, number s_size, number radius):
    cdef double tX = c_pos[0], tY = c_pos[1]
    cdef double dX, dY

    if c_pos[0] < s_x:
        tX = s_x
    elif c_pos[0] > s_x + s_size:
        tX = s_x + s_size

    if c_pos[1] < s_y:
        tY = s_y
    elif c_pos[1] > s_y + s_size:
        tY = s_y + s_size

    dX = c_pos[0] - tX
    dY = c_pos[1] - tY

    return (dX * dX) + (dY * dY) <= radius * radius


cdef _one_subchunk_coords(number x, number y, number size, int idx):
    cdef double[2] out
    out = [
        x + size * (idx & 0b1),
        y + size * ((idx & 0b10) >> 1)
    ]
    return out


cpdef (double, double) one_subchunk_coords(double[:] coords, number size, int idx):
    cdef double[2] tmp = _one_subchunk_coords(coords[0], coords[1], size / 2, idx)
    return (tmp[0], tmp[1])


cdef _subchunk_coords(number x, number y, number size):
    cdef double[4][2] out
    cdef int i
    for i in range(4):
        out[i] = _one_subchunk_coords(x, y, size, i)
    return out


cpdef list subchunk_coords(double[:] coords, number size):
    cdef list out = []
    cdef int i
    cdef double[4][2] subchunks = _subchunk_coords(coords[0], coords[1], size / 2)
    for i in range(4):
        out.append((subchunks[i][0], subchunks[i][1]))
    return out


cpdef list circle_in_subchunks(double[:] start, double[:] circle_pos, number size, number radius):
    cdef double x = start[0], y = start[1]
    cdef list out = []
    cdef int idx = 0
    size /= 2
    cdef double[4][2] subchunks = _subchunk_coords(x, y, size)


    for i in range(4):
        if circle_square_collision(subchunks[i][0], subchunks[i][1], circle_pos, size, radius):
            out.append(idx)
        idx += 1

    return out
    
