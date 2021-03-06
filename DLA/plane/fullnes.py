from __future__ import annotations

from typing import Optional

from DLA.plane.base_plane import BasePlane


class CanBeFull(BasePlane):
    can_be_full: bool = True

    def set_full(self) -> None:
        if not self.full:
            self.full = True
            del self._sub_planes

    @staticmethod
    def _check_is_full(v: Optional[BasePlane]) -> bool:
        return v and v.full  # type: ignore

    def is_full(self) -> bool:
        return self.full or all(
            self._check_is_full(self._sub_planes[i]) for i in range(4)
        )

    def add_point(self, point: int) -> None:
        super().add_point(point)

        if self.is_full():
            self.set_full()


class CannotBeFull(BasePlane):
    can_be_full: bool = False

    def set_full(self) -> None:
        pass

    def is_full(self) -> bool:
        return False
