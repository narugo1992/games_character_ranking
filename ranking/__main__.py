from functools import partial

import click

from .games import GAME_NAMES
from .project import create_ranking_project
from .utils import GLOBAL_CONTEXT_SETTINGS
from .utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'ranking')


@click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Utils with ranklist.")
def cli():
    pass  # pragma: no cover


@cli.command('create', help='Create rank list.',
             context_settings={**GLOBAL_CONTEXT_SETTINGS})
@click.option('--game', '-g', 'game', type=click.Choice(GAME_NAMES), required=True,
              help='Game to create.')
@click.option('--mode', '-m', 'mode', type=click.Choice(['r18', 'safe']), default='r18',
              help='Mode and order to create.', show_default=True)
@click.option('--output', '-o', 'output_dir', type=click.Path(file_okay=False), required=True,
              help='Output path of ranklist project.')
@click.option('--number', '-n', 'number', type=int, default=10,
              help='Character count.')
@click.option('--icon_size', 'icon_size', type=int, default=150,
              help='Size of character icon (in pixels)', show_default=True)
def update(game: str, mode: str, number: int, output_dir: str, icon_size: int):
    create_ranking_project(game, output_dir, number, icon_size, mode)


if __name__ == '__main__':
    cli()
