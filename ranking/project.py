import os

from gchar.resources.pixiv import get_pixiv_illustration_count_by_character
from tabulate import tabulate
from tqdm.auto import tqdm

from .games import get_character_class, get_logo

IMAGES = 'images'


def create_ranking_project(game: str, output_dir: str, count: int = 10, image_size: int = 100, mode: str = 'r18'):
    cls, game_name = get_character_class(game)
    items = []
    for ch in cls.all(contains_extra=False):
        data = get_pixiv_illustration_count_by_character(ch)
        if not data:
            continue
        items.append((ch, *data))

    items = sorted(items, key=lambda x: (-x[2], -x[1]) if mode == 'r18' else (-x[1], -x[2]))[:count]

    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, IMAGES)
    os.makedirs(images_dir, exist_ok=True)

    markdown_file = os.path.join(output_dir, 'README.md')
    with open(markdown_file, 'w', encoding='utf-8') as f:
        print(f'# Character Ranking List of {game_name.capitalize()} [{"Safe" if mode != "r18" else "R18"}]', file=f)
        print(file=f)

        headers = ['Rank', 'Face', 'CN', 'JP', 'EN', 'All Images', 'R18 Images']
        table = []
        for rank, (ch, total_count, r18_count) in enumerate(tqdm(items), start=1):
            logo_image = get_logo(ch).resize((image_size, image_size))
            logo_filename = f'logo_{ch.enname}.png'
            logo_image_path = os.path.join(images_dir, logo_filename)
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
        print(tabulate(table, headers, tablefmt="github"), file=f)
