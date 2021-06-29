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


cdef inline double dot(double[::1] a, double[::1] b):
    return a[0] * b[0] + a[1] * b[1]


cdef double _dot_self(double[::1] a):
    return a[0] * a[0] + a[1] * a[1]


cpdef double dot_self(double[::1] a):
    return _dot_self(a)


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


cdef double[:, ::1] _subchunk_coords(double[::1] coords, double size):
    cdef double[:, ::1] out = cvarray(shape=(4, 2), itemsize=sizeof(double), format='d')
    cdef int i
    for i in range(4):
        out[i] = _one_subchunk_coords(coords, size, i)
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


cpdef array.array check_particle_outside_plane(double[::1] particle, double radius, double plane_size):
    cdef array.array out = array.array('B', (0, 0, 0, 0, 0, 0, 0, 0))
    cdef double[::1] tmp = particle.copy()
    cdef double[::1] tmp3 = particle.copy()
    cdef double tmp2 = 2.2 * radius
    cdef int i
    cdef int idx = 0
    tmp[0] = tmp2
    tmp[1] = tmp2
    tmp2 = plane_size - tmp2

    # If collides (True), it means that it's to far from the outside of main plane
    if not circle_square_collision(tmp, particle, tmp2, radius):
        tmp[0] = -plane_size
        tmp[1] = -plane_size
        
        for i in range(3):
            tmp3 = _one_subchunk_coords(tmp, plane_size, i)
            if circle_square_collision(tmp3, particle, plane_size, radius):
                out[idx] = 1
            idx += 1
        
        tmp[0] = 0
        tmp[1] = 0

        for i in range(1, 4):
            tmp3 = _one_subchunk_coords(tmp, plane_size, i)
            if circle_square_collision(tmp3, particle, plane_size, radius):
                out[idx] = 1
            idx += 1

        tmp3[0] = plane_size
        tmp3[1] = -plane_size
        if circle_square_collision(tmp3, particle, plane_size, radius):
            out[idx] = 1
        idx += 1

        tmp3[0] = -plane_size
        tmp3[1] = plane_size
        if circle_square_collision(tmp3, particle, plane_size, radius):
            out[idx] = 1
        idx += 1

    return out

@cython.cdivision(True)
cdef double calc_collision_time(double[::1] static_part, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double a = _dot_self(move_vec)
    cdef double tmp_1 = moving_part[0] - static_part[0]
    cdef double tmp_2 = moving_part[1] - static_part[1]
    cdef double b = move_vec[0] * tmp_1 + move_vec[1] * tmp_2

    cdef double c = tmp_1 * tmp_1 + tmp_2 * tmp_2 - 4 * radius * radius

    cdef double delta = b * b - c * a

    if delta < 0:
        return 2

    cdef double sqrt_delta = sqrt(delta)
    cdef double one_over_a = 1 / a

    cdef double o1 = (-b + sqrt_delta) * one_over_a
    cdef double o2 = (-b - sqrt_delta) * one_over_a

    return min(o1, o2)


cdef double check_collision_times(double[:, ::1] static_parts, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double out_time = 2
    cdef Py_ssize_t i
    cdef Py_ssize_t size = static_parts.shape[0]
    cdef double tmp_1, tmp_2

    cdef double move_range = (2 * radius + _dot_self(move_vec)) ** 2
    cdef double r2 = 4 * radius * radius

    for i in range(size):
        tmp_1 = ((moving_part[0] - static_parts[i][0]) ** 2 + (moving_part[1] - static_parts[i][1]) ** 2)
        if tmp_1 <= move_range:
            tmp_2 = calc_collision_time(static_parts[i], moving_part, move_vec, radius)
            if tmp_2 < 0 and tmp_1 >= r2:
                continue
            out_time = min(tmp_2, out_time)
    return out_time


cdef double _get_collision_time(
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
    plane_size /= 2
    
    for i in range(4):
        sub_plane = sub_planes[i]

        if sub_plane is None:
            continue

        tmp = _one_subchunk_coords(start_pos, plane_size, i)
        if circle_square_collision(tmp, area_check_center, plane_size, area_check_radius):

            if plane_size == particle_plane_size:
                tmp_1 = getattr(sub_plane, 'parts')
                k = tmp_1.shape[0]
                tmp_2 = cvarray(shape=(k, 2), itemsize=sizeof(double), format='d')

                for j in range(k):
                    tmp_2[j] = stuck_points[tmp_1[j]]

                time = min(time, check_collision_times(
                    tmp_2,
                    moving_part,
                    move_vec,
                    radius
                ))
            else:
                time = min(time, _get_collision_time(
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
cpdef double get_collision_time(object plane, double particle_plane_size, double[::1] moving_part, double[::1] move_vec, double radius):
    cdef double[::1] area_check_center = moving_part.copy()
    cdef double area_check_radius = sqrt(_dot_self(move_vec)) / 2 + 1.5 * radius
    cdef double[::1] start_pos = getattr(plane, 'start_pos')
    cdef double plane_size = getattr(plane, 'size')
    cdef double[:, ::1] stuck_points = getattr(getattr(plane, '_stuck_points'), 'view')
    area_check_center[0] += move_vec[0] / 2
    area_check_center[1] += move_vec[1] / 2

    return _get_collision_time(plane, particle_plane_size, start_pos, plane_size, stuck_points, moving_part, move_vec, radius, area_check_center, area_check_radius)
