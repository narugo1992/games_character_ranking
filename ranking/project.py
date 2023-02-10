import os
import re
from typing import Optional, List, Collection, Tuple

from gchar.resources.pixiv import query_pixiv_illustration_count_by_character
from hbutils.string import plural_word
from tabulate import tabulate
from tqdm.auto import tqdm

from .games import get_character_class, get_logo, GAME_NAMES, get_character_title

IMAGES = 'images'


def create_ranking_table(game: str, icon_dir: str, count: int = 10, icon_size: int = 100, mode: str = 'r18',
                         existing_logo_filenames: Optional[Collection[str]] = None) -> Tuple[int, str, List[str]]:
    cls, game_name = get_character_class(game)
    items = []
    for ch in cls.all(contains_extra=False):
        data = query_pixiv_illustration_count_by_character(ch)
        if not data:
            continue
        items.append((ch, *data))

    items = sorted(items, key=lambda x: (-x[2], -x[1]) if mode == 'r18' else (-x[1], -x[2]))[:count]

    headers = ['Rank', 'Face', 'CN', 'JP', 'EN', 'All Images', 'R18 Images']
    table = []
    existing_filenames = set(existing_logo_filenames or [])
    for rank, (ch, total_count, r18_count) in enumerate(tqdm(items), start=1):
        logo_image = get_logo(ch, min_size=icon_size).resize((icon_size, icon_size))
        logo_filename = f'logo_{ch.enname}.png'
        index = 1
        while logo_filename in existing_filenames:
            index += 1
            logo_filename = f'logo_{ch.enname}_{index}.png'
        existing_filenames.add(logo_filename)
        logo_image_path = os.path.join(icon_dir, logo_filename)
        logo_image.save(logo_image_path)

        logo_md_element = f'![{ch.enname}]({os.path.join(".", IMAGES, logo_filename)})'
        table.append((
            rank,
            logo_md_element,
            str(ch.cnname) if ch.cnname else '',
            str(ch.jpname) if ch.jpname else '',
            str(ch.enname) if ch.enname else '',
            total_count,
            r18_count,
        ))

    return len(items), tabulate(table, headers, tablefmt="github"), list(existing_logo_filenames)


def _capitalize(text: str):
    return re.sub('\\b(?P<word>\\w+)\\b', lambda x: x.group('word').capitalize(), text)


def create_ranking_project(game: str, output_dir: str, count: int = 10, icon_size: int = 100, mode: str = 'r18'):
    game_name = get_character_title(game)

    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, IMAGES)
    os.makedirs(images_dir, exist_ok=True)

    markdown_file = os.path.join(output_dir, 'README.md')
    with open(markdown_file, 'w', encoding='utf-8') as f:
        print(f'# Character Ranking List of {_capitalize(game_name)} [{"Safe" if mode != "r18" else "R18"}]', file=f)
        print(file=f)
        print('[![Last Updated](https://img.shields.io/endpoint?'
              'url=https://gist.githubusercontent.com/narugo1992/'
              '254442dea2e77cf46366df97f499242f/raw/data_last_update.json)]'
              '(https://huggingface.co/datasets/deepghs/game_characters)', file=f)
        print(file=f)

        cnt, table_text, _ = create_ranking_table(game, images_dir, count, icon_size, mode, [])

        print(f'{game_name.capitalize()} game character {"safe" if mode != "r18" else "r18"} '
              f'picture number ranking on pixiv, the top {plural_word(cnt, "character")}. ', file=f)
        print(file=f)

        print(table_text, file=f)


def create_homepage_project(output_dir: str, games: Optional[List[str]] = None,
                            count: int = 5, icon_size: int = 100, mode: str = 'r18'):
    games = games or GAME_NAMES

    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, IMAGES)
    os.makedirs(images_dir, exist_ok=True)

    markdown_file = os.path.join(output_dir, 'README.md')
    _existing_image_filenames = []
    with open(markdown_file, 'w', encoding='utf-8') as f:
        print(f'# games_character_ranking', file=f)
        print(file=f)
        print('[![Last Updated](https://img.shields.io/endpoint?'
              'url=https://gist.githubusercontent.com/narugo1992/'
              '254442dea2e77cf46366df97f499242f/raw/data_last_update.json)]'
              '(https://huggingface.co/datasets/deepghs/game_characters)', file=f)
        print(file=f)
        print('Pixiv-based Game Characters Ranking', file=f)
        print(file=f)
        print('The data is refreshed every day.', file=f)
        print(file=f)

        games_tqdm = tqdm(games)
        for game in games_tqdm:
            game_title = get_character_title(game)
            games_tqdm.set_description(game_title)

            print(f'## {_capitalize(game_title)}', file=f)
            print(file=f)
            print(f'Top rank list of {game_title} '
                  f'( Full Version: [Safe](https://github.com/narugo1992/games_character_ranking/tree/{game}_safe) '
                  f'| [R18](https://github.com/narugo1992/games_character_ranking/tree/{game}_r18) )', file=f)
            print(file=f)

            _, table_text, _existing_image_filenames = create_ranking_table(
                game, images_dir, count, icon_size, mode, _existing_image_filenames)
            print(table_text, file=f)
            print(file=f)
