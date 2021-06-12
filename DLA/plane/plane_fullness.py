from __future__ import annotations

from typing import Optional

from DLA.plane.base_plane import BasePlane


class FullablePlane(BasePlane):
    can_be_full: bool = True

    def set_full(self) -> None:
        self.full = True
        del self._sub_planes

    @staticmethod
    def _check_is_full(v: Optional[BasePlane]) -> bool:
        return v and v.full  # type: ignore

    def are_full(self) -> bool:
        return self.full or all(
            self._check_is_full(self._sub_planes[i]) for i in range(4)
        )


class NotFullablePlane(BasePlane):
    can_be_full: bool = False

    def set_full(self) -> None:
        pass

    def are_full(self) -> bool:
        return False
