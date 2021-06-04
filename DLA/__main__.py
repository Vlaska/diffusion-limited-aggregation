from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from pkgutil import get_data
from typing import Any, Dict, List, Optional, Union

import click
import yaml

import DLA


def load_config(
    path: Optional[str], module: str, file: str, multi: bool = False
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:

    config_str: str
    if path is None:
        _config_data = get_data(module, file)
        if _config_data:
            config_str = _config_data.decode('utf-8')
        else:
            raise Exception("Missing configuration data")
    elif path == '-':
        with click.get_text_stream('stdin', 'utf-8') as f:
            config_str = f.read(-1)
    else:
        config_str = Path(path).read_text('utf-8')
    if multi:
        return list(yaml.full_load_all(config_str))
    else:
        return yaml.full_load(config_str)


@click.group()
def cli() -> None:
    pass


@cli.command()
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
    """Run Diffusion Limited Aggregations with provided configuration
    """

    # Supress pygame banner
    sys.stdout = open(os.devnull, 'w')
    try:
        import pygame  # noqa
    except ImportError:
        pass
    sys.stdout = sys.__stdout__

    config_dict = load_config(config, 'DLA', 'config.yml')
    setattr(DLA, 'config_dict', config_dict)
    from DLA.simulation import main

    main()


@cli.command()
@click.option(
    '-o', '--out',
    nargs=1, default=Path('.'), type=Path, show_default=True
)
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
def server(out: str, config: Optional[str]) -> None:
    """Run server to initialize simulations running on clients.
    """
    config_dict = load_config(config, 'DLA.server', 'server_config.yml')
    import DLA.server as s
    setattr(s, 'config_dict', config_dict)
    from DLA.server.server import server as serv
    asyncio.run(serv(out))


@cli.command()
@click.option(
    '-c', '--clients',
    nargs=1, default=1, type=int, show_default=True
)
def client(clients) -> None:
    """Start symulation based on configuration from server and return results
    to it.
    """
    from DLA.server.client import run_clients
    asyncio.run(run_clients(clients))


if __name__ == '__main__':
    cli()
