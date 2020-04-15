import cv2
import json
import math
import numpy as np
from . import config, ascension_detection as ad
from .enums import HeroAscension

ASCENSION_COLORS_WEIGHTS = {name.value: num for num, name in enumerate(HeroAscension)}

def get_resize_size():
    screen_width = 1080
    icon_size = 100
    multiplier = 1.77
    margin = 14.68927
    gutter = 22
    icon_border = 26
    return (
        math.floor((screen_width - (6 * margin) * multiplier - gutter * multiplier) / 5)
        - icon_border
    )


def cut_icon(processed_icon, icon_size):
    h_s = math.ceil(0.2 * icon_size)
    h_e = math.ceil(0.78 * icon_size)
    w_s = math.ceil(0.3 * icon_size)
    w_e = math.ceil(1 * icon_size)
    return processed_icon[h_s:h_e, w_s:w_e]


def prepare_image(image_path):
    original_image = cv2.imread(image_path)
    original_h, original_w = original_image.shape[:2]
    target_w = 1080
    target_h = round(target_w / original_w * original_h)

    base_image = cv2.resize(original_image, (target_w, target_h))
    base_h, base_w = base_image.shape[:2]
    image_cut = base_image[190 : base_h - 470, :]
    return image_cut


def prepare_icon(filename):
    icon_size = get_resize_size()
    icon = cv2.imread(str(config.RESOURCES_DIR / filename))

    icon_processed = cv2.resize(icon, (icon_size, icon_size))
    return cut_icon(icon_processed, icon_size)


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


def find_hero(base_image, filename):
    icon = prepare_icon(filename)
    res = cv2.matchTemplate(base_image, icon, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(res)[1]
    threshold = max(max_val - 0.05, 0.825)
    loc = np.where(res >= threshold)
    return zip(*loc[::-1])


def get_icon_sections(pt, image):
    sections = {
        "border": lambda img: img[pt[1] + 122 : pt[1] + 128, pt[0] : pt[0] + 40],
        "plus_border": lambda img: img[
            pt[1] + 122 : pt[1] + 128, pt[0] - 38 : pt[0] - 30
        ],
        "stars": lambda img: img[pt[1] + 90 : pt[1] + 119, pt[0] - 46 : pt[0] + 80],
        "level": lambda img: img[pt[1] - 31 : pt[1], pt[0] : pt[0] + 97],
    }

    def get_section(section):
        return sections[section](image)

    return get_section


def not_in_mask(mask, pt):
    return mask[math.ceil(pt[1] + 87 / 2), math.ceil(pt[0] + 105 / 2)] != 255


def mark_mask(mask, pt):
    mask[pt[1] : pt[1] + 87, pt[0] : pt[0] + 105] = 255


def process_hero(hero, mask, base_image):
    matches = []
    hero_locations = find_hero(base_image, hero["filename"])

    for pt in hero_locations:
        if not_in_mask(mask, pt):
            mark_mask(mask, pt)
            get_section = get_icon_sections(pt, base_image)

            ascension = ad.determine_ascension_level(
                get_section("border"), get_section("plus_border")
            )
            ascension_level = None

            if ascension == "Ascended":
                ascension_level = ad.get_ascension_level(get_section("stars"))

            level = ad.get_level(get_section("level"), hero["name"])

            matches.append(
                {
                    "name": hero["name"],
                    "faction": hero["faction"],
                    "class": hero["class"],
                    "rarity": hero["rarity"],
                    "ascension": ascension,
                    "ascensionLevel": ascension_level,
                    "level": level,
                }
            )

    return matches


def recognize_heroes(image_path, faction=None, class_name=None, include_common=None):
    heroes = load_hero_data(faction, class_name, include_common)
    base_image = prepare_image(str(config.SCREENS_DIR / image_path))
    mask = np.zeros(base_image.shape[:2], np.uint8)
    matches = []

    for hero in heroes:
        matches.extend(process_hero(hero, mask, base_image))

    return sorted(
        matches,
        key=lambda i: (
            -i["level"] if i["level"] is not None else 0,
            -ASCENSION_COLORS_WEIGHTS[i["ascension"]],
            -i["ascensionLevel"] if i["ascensionLevel"] is not None else 0,
        ),
    )
