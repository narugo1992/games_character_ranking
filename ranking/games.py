import os.path
import tempfile
import time
from typing import Union, Type, Iterator, Tuple, Optional

from PIL import Image
from gchar.games.arknights import Character as ArknightsCharacter
from gchar.games.azurlane import Character as AzurLaneCharacter
from gchar.games.base import Character, Skin
from gchar.games.dispatch.access import GAME_CHARS
from gchar.games.fgo import Character as FateGrandOrderCharacter
from gchar.games.girlsfrontline import Character as GirlsFrontLineCharacter
from gchar.games.neuralcloud import Character as NeuralCloudCharacter
from gchar.games.nikke import Character as NikkeCharacter
from gchar.games.starrail import Character as StarRailCharacter
from gchar.utils import download_file
from requests.exceptions import RequestException

_GAMES = [
    (ch, name, ch.__official_name__)
    for name, ch in GAME_CHARS.items()
]

GAME_NAMES = [name for _, name, _ in _GAMES]


def get_character_class(chname: Union[Type[Character], str]) -> Tuple[Type[Character], str]:
    for cls, name, _ in _GAMES:
        if name == chname or cls == chname:
            return cls, name

    raise ValueError(f'Unknown game - {chname!r}.')


def get_character_title(chname: Union[Type[Character], str]) -> str:
    for cls, name, title in _GAMES:
        if name == chname or cls == chname:
            return title

    raise ValueError(f'Unknown game - {chname!r}.')


def _yield_skin_default(ch: Character) -> Iterator[Skin]:
    yield from ch.skins


def _yield_skin_girlsfrontline(ch: GirlsFrontLineCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'profile' not in skin.name.lower():
            yield skin


def _yield_skin_arknights(ch: ArknightsCharacter) -> Iterator[Skin]:
    yield from ch.skins


def _yield_skin_fgo(ch: FateGrandOrderCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if '愚人节' not in skin.name and 'Grail'.lower() not in skin.name.lower():
            yield skin


def _yield_skin_neuralcloud(ch: NeuralCloudCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if '愚' not in skin.name and 'ZOO' not in skin.name:
            yield skin


def _yield_skin_azurlane(ch: AzurLaneCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'chibi' not in skin.name.lower():
            yield skin


def _yield_skin_nikke(ch: NikkeCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'anim' not in skin.name.lower():
            yield skin


def _yield_skin_starrail(ch: StarRailCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if '介绍' not in skin.name:
            yield skin


_SKIN_YIELDERS = {
    'girlsfrontline': _yield_skin_girlsfrontline,
    'fgo': _yield_skin_fgo,
    'neuralcloud': _yield_skin_neuralcloud,
    'azurlane': _yield_skin_azurlane,
    'nikke': _yield_skin_nikke,
    'starrail': _yield_skin_starrail,
}


def get_logo(ch: Character, out_threshold: float = 0.8, min_threshold: float = 0.45,
             peek_threshold: float = 0.7, min_size: int = 120) -> Optional[Image.Image]:
    from .image import find_heads
    cls, game_name = get_character_class(type(ch))
    collected_skins = []
    for skin_id, skin in enumerate(_SKIN_YIELDERS.get(game_name, _yield_skin_default)(ch)):
        with tempfile.TemporaryDirectory() as td:
            skin_file = os.path.join(td, 'skin.png')
            sleep_time = 3.0
            while True:
                try:
                    download_file(skin.selected_url, skin_file, timeout=20)
                except RequestException:
                    pass
                else:
                    if os.path.getsize(skin_file):
                        break

                time.sleep(sleep_time)
                sleep_time *= 2

            skin_image = Image.open(skin_file)
            for i, (head, score) in enumerate(find_heads(skin_image)):
                if score >= out_threshold and head.width >= min_size:
                    return head
                elif score >= min_threshold:
                    collected_skins.append((head, score, head.width, i, skin_id))

    if not collected_skins:
        return None

    collected_skins = sorted(
        collected_skins,
        key=lambda x: (x[3], -min(x[1], peek_threshold), -min(x[2], min_size * 1.5, skin_id))
    )
    return collected_skins[0][0]
