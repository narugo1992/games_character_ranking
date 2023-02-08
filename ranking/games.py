import os.path
import tempfile
from typing import Union, Type, Iterator, Tuple

from PIL import Image
from gchar.games.arknights import Character as ArknightsCharacter
from gchar.games.azurlane import Character as AzurLaneCharacter
from gchar.games.base import Character, Skin
from gchar.games.fgo import Character as FateGrandOrderCharacter
from gchar.games.genshin import Character as GenshinImpactCharacter
from gchar.games.girlsfrontline import Character as GirlsFrontLineCharacter

_GAMES = [
    (ArknightsCharacter, 'arknights'),
    (FateGrandOrderCharacter, 'fgo'),
    (AzurLaneCharacter, 'azurlane'),
    (GenshinImpactCharacter, 'genshin'),
    (GirlsFrontLineCharacter, 'girlsfrontline'),
]

GAME_NAMES = [name for _, name in _GAMES]


def get_character_class(chname: Union[Type[Character], str]) -> Tuple[Type[Character], str]:
    for cls, name in _GAMES:
        if name == chname or cls == chname:
            return cls, name

    raise ValueError(f'Unknown game - {chname!r}.')


def _yield_skin_default(ch: Character) -> Iterator[Skin]:
    yield from ch.skins


def _yield_skin_girlsfrontline(ch: GirlsFrontLineCharacter) -> Iterator[Skin]:
    for skin in ch.skins:
        if 'profile' not in skin.name.lower():
            yield skin


def _yield_skin_arknights(ch: ArknightsCharacter) -> Iterator[Skin]:
    skins = sorted(ch.skins, key=lambda x: x.name)
    yield from skins


_SKIN_YIELDERS = {
    'girlsfrontline': _yield_skin_girlsfrontline,
    'arknights': _yield_skin_arknights,
}


def get_logo(ch: Character, out_threshold: float = 0.90, min_threshold: float = 0.5,
             min_size: int = 120) -> Image.Image:
    from .image import find_heads
    cls, game_name = get_character_class(type(ch))
    collected_skins = []
    for skin in _SKIN_YIELDERS.get(game_name, _yield_skin_default)(ch):
        with tempfile.TemporaryDirectory() as td:
            skin_file = os.path.join(td, 'skin.png')
            skin.download(skin_file)

            skin_image = Image.open(skin_file)
            for head, score in find_heads(skin_image):
                if score >= out_threshold and head.width >= min_size:
                    return head
                elif score >= min_threshold:
                    collected_skins.append((head, min(score, (min_threshold + out_threshold) / 2), head.width))

    if not collected_skins:
        raise ValueError(f'No head image detected for {ch!r}.')

    collected_skins = sorted(collected_skins, key=lambda x: (-x[1], -x[2]))
    return collected_skins[0][0]
