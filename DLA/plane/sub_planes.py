from __future__ import annotations

from typing import Type

from DLA.plane.base_plane import BasePlane


class SubPlane(BasePlane):
    _new_plane_type_: Type[BasePlane]
    _alt_plane_type: Type[BasePlane]

    _size_for_alt_plane_type: float

    @property
    def _new_plane_type(self) -> Type[BasePlane]:
        try:
            return self._new_plane_type_
        except AttributeError:
            self._new_plane_type_ = (
                self._alt_plane_type
                if self.size / 2 == self._size_for_alt_plane_type
                else self.__class__
            )
            return self._new_plane_type_
