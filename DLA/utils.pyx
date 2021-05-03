#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np
cimport numpy as np
cimport cython
from cython.view cimport array as cvarray
from loguru import logger
# ctypedef np.double_t DFLOAT
# ctypedef np.npy_bool DBOOL

cdef double INF = float('inf')
cdef double NAN = float('nan')

ctypedef fused number:
    int
    long
    double


logger.add("logs/utils-{time}.log",
           format="{time} | {level} | {message}")


cdef double[:] _squared_distance(double[:, :] v):
    cdef Py_ssize_t i, size = v.shape[0]
    cdef double[:] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="d")

    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return out


cpdef np.ndarray[double, ndim=1] squared_distance(double[:, :] v):
    return np.asarray(_squared_distance(v))


cpdef does_collide(double[:, :] static_points, double[:] point, number radius):
    cdef double[:] min_dist_pos
    cdef double min_dist = INF

    cdef Py_ssize_t pos_size = static_points.shape[0]
    cdef Py_ssize_t i
    # for i in range(pos_size):
    cdef double[:] dists
        
        
    #diffs = np.abs(pos - point)
    #t = squared_distance(diffs) < (4 * radius * radius)
    #r = diffs[t].compressed()
    #stuck_pos = r.reshape((r.shape[0] // 2, 2))

    #if stuck_pos.any():
    #    return True
    return False


# cpdef test_collisions(np.ndarray[DFLOAT, ndim=2] pos, np.ndarray[DFLOAT, ndim=2] points, number radius):
cpdef test_collisions(double[:, :] pos, double[:, :] points, number radius):
    cdef Py_ssize_t i, size = points.shape[0]
    # cdef np.ndarray v
    cdef double[:] v
    cdef list out = []
    # for i, v in enumerate(points):
    for i in range(size):
        v = points[i]
        print(v[0])
        print(v[0] is NAN)
        # if not v[0] is np.ma.masked and does_collide(pos, v, radius):
        #     out.append(v)
    return out


cpdef bint in_square(double[:] a, double[:] b, double[:] point):
    return a[0] <= point[0] and point[0] <= b[0] and a[1] <= point[1] and point[1] <= b[1]


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


cdef inline double dot(double[:] a, double[:] b):
    return a[0] * b[0] + a[1] * b[1]


@cython.cdivision(True)
cdef double[:] _correct_circle_pos(double[:] new_pos, double[:] step, double[:] stuck_point, number radius):
    cdef double[:] A = step
    cdef double[:] B = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double[:] out_1 = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double[:] out_2 = cvarray(shape=(2, ), itemsize=sizeof(double), format='d')
    cdef double theta
    cdef double psi
    cdef double chi
    cdef double sqrt_delta
    cdef double a_1
    cdef double a_2

    B[0] = new_pos[0] - stuck_point[0]
    B[1] = new_pos[1] - stuck_point[1]

    theta = 2 * dot(A, B)
    psi = dot(B, B) - 4 * radius * radius
    chi = dot(A, A)

    logger.debug(f"Delta: {theta * theta - 4 * psi * chi}, Theta: {theta}, Psi: {psi}, Chi: {chi}, B: ({B[0]}, {B[1]}), new_pos: ({new_pos[0]}, {new_pos[1]}), stuck_point: ({stuck_point[0]}, {stuck_point[1]}), step: ({step[0]}, {step[1]})")

    sqrt_delta = np.sqrt(theta * theta - 4 * psi * chi)

    # Chi cannot be == 0, because that would mean, that og_point didn't move
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

    logger.debug(f"Out_1: ({out_1[0]}, {out_1[1]}), Out_2: ({out_2[0]}, {out_2[1]})")

    if dot(A, A) < dot(B, B):
        return out_1

    return out_2


cpdef np.ndarray correct_circle_pos(double[:] new_pos, double[:] step, double[:] stuck_point, number radius):
    cdef double[:] t = _correct_circle_pos(new_pos, step, stuck_point, radius)
    logger.debug(f"Value to be returned: ({t[0]}, {t[1]})")
    return np.asarray(t)
