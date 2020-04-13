import cv2
import json
import math
import numpy as np
from . import consts


def get_resize_size():
    icon_size = 100
    multiplier = 1.77
    margin = 14.68927
    gutter = 22
    icon_border = 26
    return (
        math.floor(
            (consts.SCREEN_WIDTH - (6 * margin) * multiplier - gutter * multiplier) / 5
        )
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
    target_w = consts.SCREEN_WIDTH
    target_h = round(target_w / original_w * original_h)

    base_image = cv2.resize(original_image, (target_w, target_h))
    base_h, base_w = base_image.shape[:2]
    image_cut = base_image[190 : base_h - 470, :]
    return image_cut


def prepare_icon(filename):
    icon_size = get_resize_size()
    icon = cv2.imread(str(consts.RESOURCES_DIR / filename))

    icon_processed = cv2.resize(icon, (icon_size, icon_size))
    return cut_icon(icon_processed, icon_size)


def load_hero_data(faction=None, class_name=None, include_common=None):
    filtered_heroes = []
    json_file = (consts.RESOURCES_DIR / consts.HERO_DATA_FILENAME).read_text()
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
