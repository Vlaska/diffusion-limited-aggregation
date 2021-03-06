from __future__ import annotations

import asyncio
import os
import pkgutil
import sys
from pathlib import Path
from pkgutil import get_data
from typing import Any, Dict, List, Optional, Union, cast

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

    CONFIG - simulation configuration file
    """

    # Suppress pygame banner
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
    nargs=1, default=Path('.'), type=Path, show_default=True,
    help='output folder'
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
def server(out: Path, config: Optional[str]) -> None:
    """Run server to initialize simulations running on clients.

    CONFIG - server configuration file
    """
    config_dict = load_config(config, 'DLA.server', 'server_config.yml')
    import DLA.server as s
    setattr(s, 'config_dict', config_dict)
    from DLA.server.server import server as serv
    asyncio.run(serv(out))


@cli.command()
@click.option(
    '-c', '--clients',
    nargs=1, default=1, type=int, show_default=True,
    help='number of maxiumum connections at ot once'
)
def client(clients: int) -> None:
    """Start simulation based on configuration from server and return results
    to it.
    """
    from DLA.server.client import run_clients
    asyncio.run(run_clients(clients))


@cli.command()
@click.argument(
    'sim_file',
    required=True,
    nargs=1,
    type=click.Path(
        exists=True,
        dir_okay=False,
        resolve_path=True,
        allow_dash=False
    )
)
@click.option(
    '-o',
    '--only-stuck',
    default=False,
    show_default=True,
    is_flag=True,
    help='turn off rendering of walking particles; can be toggled using space'
)
def render(sim_file: str, only_stuck: bool) -> None:
    """Render particles from past simulation.

    SIM_FILE - path to `.pickle` file
    """
    import DLA
    DLA.GREEN = (0, 0, 0)  # type: ignore
    DLA.WHITE = (151, 151, 151, 150)  # type: ignore
    from DLA import config
    config.USE_PYGAME = True  # type: ignore
    from DLA import renderer
    renderer.render(Path(sim_file), only_stuck)


@cli.command()
def configs() -> None:
    """Copy default simulation and server configuration files.

    server_config.yml - configuration file for use with `server`
    config.yml - configuration file for use with `simulate`
    """
    config_data = cast(bytes, pkgutil.get_data('DLA', 'config.yml'))
    server_config_data = cast(
        bytes, pkgutil.get_data('DLA.server', 'server_config.yml')
    )

    current_path = Path('.')

    (current_path / 'config.yml').write_bytes(config_data)
    (current_path / 'server_config.yml').write_bytes(server_config_data)

    click.echo('Copied default configuration files.')


if __name__ == '__main__':
    cli()
