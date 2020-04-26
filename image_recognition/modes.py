from enum import Enum

from . import config
from .enums import Mode

heroes_page = {
    "hero_icon": {
        "flip": False,
        "icon_size": 151,
        "icon_cut_ratios": [32, 118, 46, 151],
    },
    "sections": {
        "border": [122, 128, 0, 40],
        "plus_border": [122, 128, -38, -30],
        "stars": [90, 119, -46, 80],
        "level": [-29, 0, 1, 94],
    },
}

challenger_lineup = {
    "hero_icon": {
        "flip": True,
        "icon_size": 121,
        "icon_cut_ratios": [36, 94, 27, 121],
    },
    "sections": {
        "border": [87, 92, 0, 30],
        "plus_border": [87, 92, -23, -14],
        "stars": [58, 85, -27, 78],
        "level": [0, 0, 0, 0],
    },
}


class ModeSettings(Enum):
    HERO_ICON = "hero_icon"
    SECTIONS = "sections"


def get_mode_settings(mode: Mode, specific_config: ModeSettings):
    if mode == Mode.CHALLENGER_LINEUP:
        return challenger_lineup[specific_config.value]
    if mode == Mode.HEROES_PAGE:
        return heroes_page[specific_config.value]
