import json

from . import config
from .base_image import BaseImage
from .enums import HeroAscension
from .hero import Hero


def load_hero_data(faction=None, class_name=None, include_common=None):
    filtered_heroes = []
    json_file = (config.RESOURCES_DIR / config.HERO_DATA_FILENAME).read_text()
    heroes = json.loads(json_file)

    for hero in heroes:
        if hero["rarity"] != "Common" or include_common:
            if faction == None and class_name == None:
                filtered_heroes.append(hero)
            elif faction != None and class_name == None:
                if hero["faction"] == faction:
                    filtered_heroes.append(hero)
            elif faction == None and class_name != None:
                if hero["class"] == class_name:
                    filtered_heroes.append(hero)
            else:
                if hero["faction"] == faction and hero["class"] == class_name:
                    filtered_heroes.append(hero)

    return filtered_heroes


def recognize_heroes(filename, faction=None, class_name=None, include_common=None):
    heroes = load_hero_data(faction, class_name, include_common)
    base_image = BaseImage(filename)
    matches = []

    for hero_data in heroes:
        hero = Hero(hero_data)
        base_image.find_hero_copies(hero)
        matches.extend(hero.matches)

    return [hero.asdict() for hero in sorted(matches)]
