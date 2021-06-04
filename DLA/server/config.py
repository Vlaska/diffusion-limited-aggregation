from __future__ import annotations

from typing import Any, Dict, Final, cast

try:
    from . import config_dict
except ImportError:
    import pkgutil

    import yaml

    config_dict = list(yaml.full_load_all(
        cast(
            bytes, pkgutil.get_data('DLA.server', 'server_config.yml')
        ).decode('utf-8')
    ))


rest = config_dict[0]

CONFIG_TEMPLATE: Final[Dict[str, Any]] = config_dict[1]
START: Final[float] = rest['start']
END: Final[float] = rest['end']
STEP: Final[float] = rest['step']
NUM_OF_SAMPLES: Final[int] = rest['num_of_samples']
