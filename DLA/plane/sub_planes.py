from __future__ import annotations

from typing import Type, Iterable, Optional, List, cast

from DLA import Vec
from DLA.plane.base_plane import BasePlane
from DLA.utils import one_subchunk_coords


class SubPlane:
    _new_plane_type_: Type[BasePlane]
    _alt_plane_type: Type[BasePlane]

    _size_for_alt_plane_type: float

    _sub_planes: List[Optional[BasePlane]]
    start_pos: Vec
    size: float

    def add_sub_chunks(self, chunks: Iterable[int]) -> None:
        for i in chunks:
            if not self._sub_planes[i]:
                self._sub_planes[i] = self._new_plane_type(
                    one_subchunk_coords(self.start_pos, self.size, i),
                    self.size / 2
                )

    @property
    def _new_plane_type(self) -> Type[BasePlane]:
        try:
            return self._new_plane_type_
        except AttributeError:
            self._new_plane_type_ = (
                self._alt_plane_type
                if self.size / 2 == self._size_for_alt_plane_type
                else cast(Type[BasePlane], self.__class__)
            )
            return self._new_plane_type_
