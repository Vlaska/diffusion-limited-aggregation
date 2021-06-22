#cython: language_level=3
#cython: wraparound=False
#cython: boundscheck=False
#cython: nonecheck=False

import numpy as np

cimport cython
cimport numpy as np
from cpython cimport array
from cpython.ref cimport PyObject
from cython.view cimport array as cvarray

import array


cdef extern from "math.h":
    double sqrt(double m)


cdef double[::1] _squared_distance(double[:, ::1] v):
    cdef Py_ssize_t i, size = v.shape[0]
    cdef double[::1] out = cvarray(shape=(size, ), itemsize=sizeof(double), format="d")

    for i in range(size):
        out[i] = v[i, 0] * v[i, 0] + v[i, 1] * v[i, 1]

    return out


cpdef np.ndarray[double, ndim=1] squared_distance(double[:, ::1] v):
    return np.asarray(_squared_distance(v))


cdef bint circle_square_collision(double[::1] s_pos, double[::1] c_pos, double s_size, double radius):
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


cdef double[::1] _one_subchunk_coords(double[::1] coords, double size, int idx):
    cdef double[::1] out = coords.copy()
    out[0] += size * (idx & 0b1)
    out[1] += size * ((idx & 0b10) >> 1)
    return out


cpdef (double, double) one_subchunk_coords(double[::1] coords, double size, int idx):
    cdef double[::1] tmp = _one_subchunk_coords(coords, size / 2, idx)
    return tuple(tmp)


cdef _subchunk_coords(double[::1] coords, double size):
    cdef double[:, ::1] out = cvarray(shape=(4, 2), itemsize=sizeof(double), format='d')
    cdef int i
    for i in range(4):
        out[i] = _one_subchunk_coords(coords, size, i)
    return out


cpdef list subchunk_coords(double[::1] coords, double size):
    cdef list out = []
    cdef int i
    cdef double[:, ::1] subchunks = _subchunk_coords(coords, size / 2)
    for i in range(4):
        out.append((subchunks[i][0], subchunks[i][1]))
    return out


cpdef list circle_in_subchunks(double[::1] start, double[::1] circle_pos, double size, double radius):
    cdef list out = []
    cdef int idx = 0
    size /= 2
    cdef double[:, ::1] subchunks = _subchunk_coords(start, size)

    for i in range(4):
        if circle_square_collision(subchunks[i], circle_pos, size, radius):
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
    cdef double[::1] A = step.copy()
    cdef double[::1] B = new_pos.copy()
    cdef double[::1] out_1 = stuck_point.copy()
    cdef double[::1] out_2 = stuck_point.copy()
    cdef double theta
    cdef double psi
    cdef double chi
    cdef double sqrt_delta
    cdef double a_1
    cdef double a_2

    A[:] = step

    B[0] -= stuck_point[0]
    B[1] -= stuck_point[1]

    theta = 2 * dot(A, B)
    psi = _dot_self(B) - 4 * radius * radius
    chi = _dot_self(A)

    sqrt_delta = sqrt(theta * theta - 4 * psi * chi)

    # Chi cannot be == 0, because that would mean, that new_pos didn't change
    # therefore would not collide with stuck_point
    a_1 = (-theta + sqrt_delta) / (2 * chi)
    a_2 = (-theta - sqrt_delta) / (2 * chi)

    out_1[0] += B[0] + a_1 * A[0]
    out_1[1] += B[1] + a_1 * A[1]
    out_2[0] += B[0] + a_2 * A[0]
    out_2[1] += B[1] + a_2 * A[1]

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
    cdef double[::1] tmp
    cdef double r_sqruared = radius * radius
    for i in range(4):
        tmp = _one_subchunk_coords(pos, size, i)
        tmp[0] -= c_pos[0]
        tmp[1] -= c_pos[1]
        if _dot_self(tmp) > r_sqruared:
            return False
    return True

@cython.cdivision(True)
cdef double _get_collision_time(double[::1] static_part, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double a = _dot_self(move_vec)
    cdef double tmp_1 = moving_part[0] - static_part[0]
    cdef double tmp_2 = moving_part[1] - static_part[1]
    cdef double b = move_vec[0] * tmp_1 + move_vec[1] * tmp_2
    # cdef double c = _dot_self(static_part) + _dot_self(moving_part) - 4 * radius * radius
    cdef double c = tmp_1 * tmp_1 + tmp_2 * tmp_2 - 4 * radius * radius

    cdef double delta = b * b - c * a
    # print(a, b, c, delta)
    if delta < 0:
        return 2

    cdef double sqrt_delta = sqrt(delta)
    cdef double one_over_a = 1 / a

    cdef double o1 = (-b + sqrt_delta) * one_over_a
    cdef double o2 = (-b - sqrt_delta) * one_over_a

    return min(o1, o2)


cpdef double get_collision_time(double[:, ::1] static_parts, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double out_time = 2
    cdef Py_ssize_t i
    cdef Py_ssize_t size = static_parts.shape[0]
    cdef double tmp_1, tmp_2

    cdef double move_range = (2 * radius + _dot_self(move_vec)) ** 2
    cdef double r2 = 4 * radius * radius

    for i in range(size):
        tmp_1 = ((moving_part[0] - static_parts[i][0]) ** 2 + (moving_part[1] - static_parts[i][1]) ** 2)
        if tmp_1 <= move_range:
            tmp_2 = _get_collision_time(static_parts[i], moving_part, move_vec, radius)
            if tmp_2 < 0 and tmp_1 >= r2:
                continue
            out_time = min(tmp_2, out_time)
    return out_time


cdef double _new_get_collision_time(
    object plane,
    double particle_plane_size,
    double[::1] start_pos,
    double plane_size,
    double[:, ::1] stuck_points,
    double[::1] moving_part,
    double[::1] move_vec,
    double radius,
    double[::1] area_check_center,
    double area_check_radius
):
    cdef double time = 2.0
    cdef list sub_planes = getattr(plane, '_sub_planes')
    cdef Py_ssize_t i, j, k
    cdef double[::1] tmp
    cdef unsigned int[::1] tmp_1
    cdef double[:, ::1] tmp_2
    cdef object sub_plane
    # print(circle_in_subchunks(start_pos, area_check_center, plane_size, area_check_radius))
    plane_size /= 2

    cdef double t1, t2

    # print('**************************')
    
    for i in range(4):
        sub_plane = sub_planes[i]

        if sub_plane is None:
            continue

        tmp = _one_subchunk_coords(start_pos, plane_size, i)
        if circle_square_collision(tmp, area_check_center, plane_size, area_check_radius):

            if plane_size == particle_plane_size:
                # print('Particle plane', 'start_pos:', tuple(tmp), 'size:', plane_size)
                tmp_1 = getattr(sub_plane, 'parts')
                k = tmp_1.shape[0]
                tmp_2 = cvarray(shape=(k, 2), itemsize=sizeof(double), format='d')


                for j in range(k):
                    # print('Added point to check:', tuple(stuck_points[tmp_1[j]]), 'start_pos:', start_pos, 'plane_size', plane_size)
                    tmp_2[j] = stuck_points[tmp_1[j]]


                # print('Old way')
                # t1 = get_collision_time(
                #     stuck_points,
                #     moving_part,
                #     move_vec,
                #     radius
                # )
                # print('New way')
                t2 = get_collision_time(
                    tmp_2,
                    moving_part,
                    move_vec,
                    radius
                )
                # if t1 != t2:
                #     print(k, t1, t2, tuple(area_check_center), area_check_radius, tuple(moving_part), tuple(move_vec))
                #     for j in range(k):
                #         print('Values of points:', tuple(stuck_points[tmp_1[j]]), tuple(tmp_2[j]))

                # time = min(time, get_collision_time(
                #     stuck_points,
                #     moving_part,
                #     move_vec,
                #     radius
                # ))
                time = min(time, t2)
            else:
                # print('Normal plane', 'start_pos:', tuple(tmp), 'size:', plane_size)
                time = min(time, _new_get_collision_time(
                    sub_plane,
                    particle_plane_size,
                    tmp,
                    plane_size,
                    stuck_points,
                    moving_part,
                    move_vec,
                    radius,
                    area_check_center,
                    area_check_radius
                ))

    return time


@cython.cdivision(True)
cpdef double new_get_collision_time(object plane, double particle_plane_size, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double[::1] area_check_center = moving_part.copy()
    cdef double area_check_radius = sqrt(_dot_self(move_vec)) / 2 + 1.5 * radius
    cdef double[::1] start_pos = getattr(plane, 'start_pos')
    cdef double plane_size = getattr(plane, 'size')
    cdef double[:, ::1] stuck_points = getattr(getattr(plane, '_stuck_points'), 'view')
    area_check_center[0] += move_vec[0] / 2
    area_check_center[1] += move_vec[1] / 2

    return _new_get_collision_time(plane, particle_plane_size, start_pos, plane_size, stuck_points, moving_part, move_vec, radius, area_check_center, area_check_radius)
