from __future__ import annotations
import asyncio

import os
import sys
from pathlib import Path
from pkgutil import get_data
from typing import Optional

import click
import yaml

import DLA


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


@cli.command()
@click.option(
    '-o', '--out',
    nargs=1, default=Path('.'), type=Path, show_default=True
)
def server(out: Path) -> None:
    """Run server to initialize simulations running on clients.
    """
    from DLA.server import server
    asyncio.run(server(out))


@cli.command()
@click.option(
    '-c', '--clients',
    nargs=1, default=1, type=int, show_default=True
)
def client(clients) -> None:
    """Start symulation based on configuration from server and return results
    to it.
    """
    from DLA.server import run_clients
    asyncio.run(run_clients(clients))


if __name__ == '__main__':
    # Supress pygame banner
    sys.stdout = open(os.devnull, 'w')
    try:
        import pygame  # noqa
    except ImportError:
        pass
    sys.stdout = sys.__stdout__
    cli()
