from __future__ import annotations

from typing import Any, Dict, Final

from DLA.types import RGB, RGBA, Vec, Vec2

confg_dict: Dict[str, Any]

BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
PINK: Final[RGB] = (255, 0, 255)
RED: Final[RGB] = (255, 0, 0)
GREEN: Final[RGB] = (0, 255, 0)
LIGHT_GRAY: Final[RGBA] = (66, 66, 66, 100)

__all__ = ['RGB', 'Vec', 'Vec2', ]
