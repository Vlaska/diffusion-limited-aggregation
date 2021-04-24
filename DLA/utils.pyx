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


cdef class ChunkIndex:
    cdef int size
    cdef int[:] _chunks

    def __init__(self):
        self.size = 0
        self._chunks = cvarray(shape=(4, ), itemsize=sizeof(int), format="i")

    def set_chunks(self, int[:] chunks):
        for i in chunks:
            self.set_chunk(i)

    def set_chunk(self, int chunk):
        self._chunks[chunk] = 1
        self.size += 1

    def get_result(self):
        # cdef int[:] out = cvarray(shape=(self.size, ), itemsize=sizeof(int), format="i")
        cdef np.ndarray[int, ndim=1] out = np.empty(self.size, dtype=int)
        cdef int idx = 0
        cdef int chunk_idx = 0
        cdef int i
        for i in self._chunks:
            if i:
                out[idx] = chunk_idx
                idx += 1
            chunk_idx += 1
        return out


#cpdef get_chunk_indexes(double[:] pos, double[:] start_pos, double size):
    # cdef int[:] out = cvarray
    # cdef int
#    return 0
