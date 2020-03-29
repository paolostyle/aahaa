import cv2
import json
import math
import numpy as np


def get_resize_size(screen_width):
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
    new_h, new_w = (base_h - 190 - 470, base_w)
    image_cut = base_image[190 : base_h - 470, 0:new_w]
    return (image_cut, new_h, new_w)


def prepare_icon(hero_name, base_width):
    icon_size = get_resize_size(base_width)
    icon = cv2.imread(f"../heroes/images/{hero_name}.jpg")
    icon_processed = cv2.resize(icon, (icon_size, icon_size))
    icon_cut = cut_icon(icon_processed, icon_size)
    h, w = icon_cut.shape[:2]

    return (icon_cut, h, w)


def load_hero_data(faction=None, class_name=None):
    filtered_heroes = []
    with open("../heroes/heroData.json") as json_file:
        heroes = json.load(json_file)
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
