from __future__ import annotations

from typing import Any, Dict, Final, cast

try:
    from . import config_dict
except ImportError:
    import pkgutil

    import yaml

    config_dict = yaml.full_load(
        cast(
            bytes, pkgutil.get_data('DLA.server', 'server_config.yml')
        ).decode('utf-8')
    )


server_config = config_dict['server']

CONFIG_TEMPLATE: Final[Dict[str, Any]] = config_dict['simulation']
START: Final[float] = server_config['start']
END: Final[float] = server_config['end']
STEP: Final[float] = server_config['step']
NUM_OF_SAMPLES: Final[int] = server_config['num_of_samples']
TIMEOUT: Final[int] = server_config['wait_for']

# Client breaks, when something else beside output file's name is printed to stdout.
CONFIG_TEMPLATE['display']['print_results'] = False

