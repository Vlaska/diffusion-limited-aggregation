#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np

cimport cython
cimport numpy as np
from cython.view cimport array as cvarray


cdef double[::1] _squared_distance(double[:, ::1] v):
    cdef Py_ssize_t i, size = v.shape[0]
    cdef double[::1] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="d")

    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return out


cpdef np.ndarray[double, ndim=1] squared_distance(double[:, ::1] v):
    return np.asarray(_squared_distance(v))


cdef bint circle_square_collision(double s_x, double s_y, double[::1] c_pos, double s_size, double radius):
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

    return (dX * dX) + (dY * dY) < radius * radius


cdef _one_subchunk_coords(double x, double y, double size, int idx):
    cdef double[2] out
    out = [
        x + size * (idx & 0b1),
        y + size * ((idx & 0b10) >> 1)
    ]
    return out


cpdef (double, double) one_subchunk_coords(double[::1] coords, double size, int idx):
    cdef double[2] tmp = _one_subchunk_coords(coords[0], coords[1], size / 2, idx)
    return (tmp[0], tmp[1])


cdef _subchunk_coords(double x, double y, double size):
    cdef double[4][2] out
    cdef int i
    for i in range(4):
        out[i] = _one_subchunk_coords(x, y, size, i)
    return out


cpdef list subchunk_coords(double[::1] coords, double size):
    cdef list out = []
    cdef int i
    cdef double[4][2] subchunks = _subchunk_coords(coords[0], coords[1], size / 2)
    for i in range(4):
        out.append((subchunks[i][0], subchunks[i][1]))
    return out


cpdef list circle_in_subchunks(double[::1] start, double[::1] circle_pos, double size, double radius):
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


cdef inline double dot(double[::1] a, double[::1] b):
    return a[0] * b[0] + a[1] * b[1]


cdef double _dot_self(double[::1] a):
    return a[0] * a[0] + a[1] * a[1]


cpdef double dot_self(double[::1] a):
    return _dot_self(a)


@cython.cdivision(True)
cdef double[::1] _correct_circle_pos(double[::1] new_pos, double[::1] step, double[::1] stuck_point, double radius):
    cdef double[::1] A = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double[::1] B = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double[::1] out_1 = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double[::1] out_2 = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double theta
    cdef double psi
    cdef double chi
    cdef double sqrt_delta
    cdef double a_1
    cdef double a_2

    A[:] = step

    B[0] = new_pos[0] - stuck_point[0]
    B[1] = new_pos[1] - stuck_point[1]

    theta = 2 * dot(A, B)
    psi = _dot_self(B) - 4 * radius * radius
    chi = _dot_self(A)

    sqrt_delta = np.sqrt(theta * theta - 4 * psi * chi)

    # Chi cannot be == 0, because that would mean, that new_pos didn't change
    # therefore would not collide with stuck_point
    a_1 = (-theta + sqrt_delta) / (2 * chi)
    a_2 = (-theta - sqrt_delta) / (2 * chi)

    out_1[0] = stuck_point[0] + B[0] + a_1 * A[0]
    out_1[1] = stuck_point[1] + B[1] + a_1 * A[1]
    out_2[0] = stuck_point[0] + B[0] + a_2 * A[0]
    out_2[1] = stuck_point[1] + B[1] + a_2 * A[1]

    A[0] = out_1[0] - new_pos[0] + step[0]
    A[1] = out_1[1] - new_pos[1] + step[1]
    B[0] = out_2[0] - new_pos[0] + step[0]
    B[1] = out_2[1] - new_pos[1] + step[1]

    if _dot_self(A) > _dot_self(B):
        out_1 = out_2

    # Shorthen step to end at the new position (in place)
    step[0] = step[0] - out_1[0] + new_pos[0]
    step[1] = step[1] - out_1[1] + new_pos[1]

    return out_1


cpdef np.ndarray[double, ndim=1] correct_circle_pos(double[::1] new_pos, double[::1] step, double[::1] stuck_point, double radius):
    return np.asarray(_correct_circle_pos(new_pos, step, stuck_point, radius))


cpdef bint is_in_circle(double[::1] pos, double[::1] c_pos, double size, double radius):
    cdef double[2] tmp
    cdef double r_sqruared = radius * radius
    for i in range(4):
        tmp = _one_subchunk_coords(pos[0], pos[1], size, i)
        tmp[0] -= c_pos[0]
        tmp[1] -= c_pos[1]
        if _dot_self(tmp) > r_sqruared:
            return False
    return True
