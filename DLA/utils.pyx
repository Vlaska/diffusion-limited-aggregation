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


cdef bint circle_square_collision(double[::1] square_coords, double[::1] particle_pos, double square_size, double radius):
    cdef double tX = particle_pos[0], tY = particle_pos[1]
    cdef double dX, dY

    if particle_pos[0] < square_coords[0]:
        tX = square_coords[0]
    elif particle_pos[0] > square_coords[0] + square_size:
        tX = square_coords[0] + square_size

    if particle_pos[1] < square_coords[1]:
        tY = square_coords[1]
    elif particle_pos[1] > square_coords[1] + square_size:
        tY = square_coords[1] + square_size

    dX = particle_pos[0] - tX
    dY = particle_pos[1] - tY

    return (dX * dX) + (dY * dY) < radius * radius


cdef double[::1] _one_sub_plane_coords(double[::1] coords, double size, int idx):
    cdef double[::1] out = coords.copy()
    out[0] += size * (idx & 0b1)
    out[1] += size * ((idx & 0b10) >> 1)
    return out


cpdef (double, double) one_sub_plane_coords(double[::1] coords, double size, int idx):
    cdef double[::1] tmp = _one_sub_plane_coords(coords, size / 2, idx)
    return tuple(tmp)


cdef double[:, ::1] _sub_plane_coords(double[::1] coords, double size):
    cdef double[:, ::1] out = cvarray(shape=(4, 2), itemsize=sizeof(double), format='d')
    cdef int i
    for i in range(4):
        out[i] = _one_sub_plane_coords(coords, size, i)
    return out


cpdef list circle_in_sub_plane(double[::1] sub_plane_coords, double[::1] circle_pos, double size, double radius):
    cdef list out = []
    cdef int idx = 0
    size /= 2
    cdef double[:, ::1] sub_planes = _sub_plane_coords(sub_plane_coords, size)

    for i in range(4):
        if circle_square_collision(sub_planes[i], circle_pos, size, radius):
            out.append(idx)
        idx += 1

    return out


cpdef bint is_in_circle(double[::1] pos, double[::1] particle_pos, double size, double radius):
    cdef double[::1] tmp
    cdef double r_squared = radius * radius
    for i in range(4):
        tmp = _one_sub_plane_coords(pos, size, i)
        tmp[0] -= particle_pos[0]
        tmp[1] -= particle_pos[1]
        if _dot_self(tmp) > r_squared:
            return False
    return True


cpdef array.array check_particle_outside_plane(double[::1] particle, double radius, double plane_size):
    cdef array.array out = array.array('B', (0, 0, 0, 0, 0, 0, 0, 0, 0))
    cdef double[::1] plane_start_coords = particle.copy()
    cdef double[::1] sub_plane_coords = particle.copy()
    cdef double helper = 2.2 * radius
    cdef int i
    cdef int idx = 0
    plane_start_coords[0] = helper
    plane_start_coords[1] = helper
    helper = plane_size - helper

    # If collides (True), it means that it's to far from the outside of main plane
    if not circle_square_collision(plane_start_coords, particle, helper, radius):
        plane_start_coords[0] = -plane_size
        plane_start_coords[1] = -plane_size
        
        for i in range(3):
            sub_plane_coords = _one_sub_plane_coords(plane_start_coords, plane_size, i)
            if circle_square_collision(sub_plane_coords, particle, plane_size, radius):
                out[idx] = 1
                out[8] = 1
            idx += 1
        
        plane_start_coords[0] = 0
        plane_start_coords[1] = 0

        for i in range(1, 4):
            sub_plane_coords = _one_sub_plane_coords(plane_start_coords, plane_size, i)
            if circle_square_collision(sub_plane_coords, particle, plane_size, radius):
                out[idx] = 1
                out[8] = 1
            idx += 1

        sub_plane_coords[0] = plane_size
        sub_plane_coords[1] = -plane_size
        if circle_square_collision(sub_plane_coords, particle, plane_size, radius):
            out[idx] = 1
            out[8] = 1
        idx += 1

        sub_plane_coords[0] = -plane_size
        sub_plane_coords[1] = plane_size
        if circle_square_collision(sub_plane_coords, particle, plane_size, radius):
            out[idx] = 1
            out[8] = 1

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
    cdef double distance_between_particles
    cdef double time_to_collision

    cdef double move_range = (2 * radius + _dot_self(move_vec)) ** 2
    cdef double r2 = 4 * radius * radius

    for i in range(size):
        distance_between_particles = ((moving_part[0] - static_parts[i][0]) ** 2 + (moving_part[1] - static_parts[i][1]) ** 2)
        if distance_between_particles <= move_range:
            time_to_collision = calc_collision_time(static_parts[i], moving_part, move_vec, radius)
            if time_to_collision < 0 and distance_between_particles >= r2:
                continue
            out_time = min(time_to_collision, out_time)
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
    cdef double[::1] sub_plane_coords
    cdef unsigned int[::1] particles_in_sub_plane
    cdef double[:, ::1] can_collide_with
    cdef object sub_plane
    plane_size /= 2
    
    for i in range(4):
        sub_plane = sub_planes[i]

        if sub_plane is None:
            continue

        sub_plane_coords = _one_sub_plane_coords(start_pos, plane_size, i)
        if circle_square_collision(sub_plane_coords, area_check_center, plane_size, area_check_radius):

            if plane_size == particle_plane_size:
                particles_in_sub_plane = getattr(sub_plane, 'parts')
                k = particles_in_sub_plane.shape[0]
                can_collide_with = cvarray(shape=(k, 2), itemsize=sizeof(double), format='d')

                for j in range(k):
                    can_collide_with[j] = stuck_points[particles_in_sub_plane[j]]

                time = min(time, check_collision_times(
                    can_collide_with,
                    moving_part,
                    move_vec,
                    radius
                ))
            else:
                time = min(time, _get_collision_time(
                    sub_plane,
                    particle_plane_size,
                    sub_plane_coords,
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
