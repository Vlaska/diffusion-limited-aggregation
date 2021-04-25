from __future__ import annotations

from pkgutil import get_data
from typing import Final

import yaml

from DLA.types import RGB, Vec, Vec2


_config_data = get_data('DLA', 'config.yml')
if _config_data:
    config = yaml.full_load(_config_data.decode('utf-8'))
else:
    raise Exception("Missing configuration data")

BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
PINK: Final[RGB] = (255, 0, 255)
RED: Final[RGB] = (255, 0, 0)
GREEN: Final[RGB] = (0, 255, 0)

__all__ = ['RGB', 'Vec', 'Vec2', ]
