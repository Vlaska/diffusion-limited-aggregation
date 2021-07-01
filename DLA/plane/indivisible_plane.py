from typing import Iterable, List, Optional

from DLA.plane.fullnes import CanBeFull


class IndivisiblePlane(CanBeFull):
    _sub_planes: List[Optional[bool]]  # type: ignore

    def add_sub_planes(self, planes: Iterable[int]) -> None:
        for i in planes:
            self._sub_planes[i] = True

    def add_point(self, point: int) -> None:
        sub_planes = self._add_point(point)

        if sub_planes is None:
            return

        if len(self) == 4:
            self.set_full()

    def is_full(self) -> bool:
        return self.full
