import math
from functools import partial
from typing import List

import click
from ditk import logging

from .games import GAME_NAMES, _GAMES
from .project import create_ranking_project, create_homepage_project
from .utils import GLOBAL_CONTEXT_SETTINGS
from .utils import print_version as _origin_print_version

print_version = partial(_origin_print_version, 'ranking')

GAME_CLASSES = {name: cls for cls, name, _ in _GAMES}


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
@click.option('--icon_size', 'icon_size', type=int, default=120,
              help='Size of character icon (in pixels)', show_default=True)
@click.option('--recent_days', 'recent_days', type=int, default=240,
              help='Recent days for recent ranking.', show_default=True)
@click.option('--min_recent_count', 'min_recent_count', type=int, default=25,
              help='Minimum recent character count in recent ranking.', show_default=True)
def create(game: str, mode: str, number: int, output_dir: str, icon_size: int,
           recent_days: int, min_recent_count: int):
    logging.try_init_root(logging.INFO)
    create_ranking_project(game, output_dir, number, icon_size, mode, min_recent_count, f'{recent_days} days')


@cli.command('crec', help='Recommended count for ranklist.')
@click.option('--game', '-g', 'game', type=click.Choice(GAME_NAMES), required=True,
              help='Update data of given game from huggingface. '
                   'All games will be updated when not given.')
@click.option('--ratio', '-r', 'ratio', type=float, default=0.2,
              help='Ratio of all characters (not including extra characters)', show_default=True)
@click.option('--unit', '-u', 'unit', type=int, default=5,
              help='Unit of all characters.', show_default=True)
@click.option('--min', '-m', 'min_count', type=int, default=40,
              help='Minimum count of ranklist.', show_default=True)
def crec(game: str, ratio: float, unit: int, min_count: int):
    logging.try_init_root(logging.INFO)
    game_cls = GAME_CLASSES[game]
    all_count = len(game_cls.all(contains_extra=False))
    exact_count = all_count * ratio
    aligned_count = int(math.ceil(exact_count / unit) * unit)
    final_count = max(min_count, aligned_count)
    print(final_count)


@cli.command('relocal', help='Regenerate the local project.')
@click.option('--game', '-g', 'games', type=click.Choice(GAME_NAMES), multiple=True, default=None,
              help='Update data of given game from huggingface. '
                   'All games will be updated when not given.', show_default=True)
@click.option('--mode', '-m', 'mode', type=click.Choice(['r18', 'safe']), default='safe',
              help='Mode and order to create.', show_default=True)
@click.option('--output', '-o', 'output_dir', type=click.Path(file_okay=False), default='.',
              help='Output path of ranklist project.')
@click.option('--number', '-n', 'number', type=int, default=5,
              help='Character count.')
@click.option('--icon_size', 'icon_size', type=int, default=120,
              help='Size of character icon (in pixels)', show_default=True)
@click.option('--recent_days', 'recent_days', type=int, default=240,
              help='Recent days for recent ranking.', show_default=True)
@click.option('--min_recent_count', 'min_recent_count', type=int, default=25,
              help='Minimum recent character count in recent ranking.', show_default=True)
def relocal(games: List[str], mode: str, number: int, output_dir: str, icon_size: int,
            recent_days: int, min_recent_count: int):
    logging.try_init_root(logging.INFO)
    create_homepage_project(output_dir, games, number, icon_size, mode, min_recent_count, f'{recent_days} days')


if __name__ == '__main__':
    cli()
