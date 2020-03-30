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
        math.floor((consts.SCREEN_WIDTH - (6 * margin) * multiplier - gutter * multiplier) / 5)
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


def prepare_icon(hero_name):
    icon_size = get_resize_size()
    icon = cv2.imread(str(consts.RESOURCES_DIR / f"{hero_name}.jpg"))

    icon_processed = cv2.resize(icon, (icon_size, icon_size))
    icon_cut = cut_icon(icon_processed, icon_size)

    return icon_cut, *icon_cut.shape[:2]


def load_hero_data(faction=None, class_name=None):
    filtered_heroes = []
    json_file = (consts.RESOURCES_DIR / consts.HERO_DATA_FILENAME).read_text()
    heroes = json.loads(json_file)

    for hero in heroes:
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
