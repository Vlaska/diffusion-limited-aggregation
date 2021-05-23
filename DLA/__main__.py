from __future__ import annotations

from pathlib import Path
from pkgutil import get_data
from typing import Optional

import click
import yaml

import DLA


@click.command()
@click.argument(
    'config',
    required=False,
    nargs=1,
    type=click.Path(
        exists=True,
        dir_okay=False,
        resolve_path=True,
        allow_dash=True
    )
)
def simulate(config: Optional[str]) -> None:
    config_str: str
    if config is None:
        _config_data = get_data('DLA', 'config.yml')
        if _config_data:
            config_str = _config_data.decode('utf-8')
        else:
            raise Exception("Missing configuration data")
    elif config == '-':
        with click.get_text_stream('stdin', 'utf-8') as f:
            config_str = f.read(-1)
    else:
        config_str = Path(config).read_text('utf-8')
    config_dict = yaml.full_load(config_str)
    setattr(DLA, 'config_dict', config_dict)
    from DLA.simulation import main

    main()


if __name__ == '__main__':
    simulate()
