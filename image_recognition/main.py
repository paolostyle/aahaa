import cv2
import json
import math
import numpy as np
import pytesseract
from tools import image_processing as ip, consts
from tools.hero_recognition import prepare_icon, prepare_image, load_hero_data
from tools.debug_utils import clear_debug, draw_rect, save_img, save_result
from tools.ascension_detection import determine_ascension_level


def progress(hero, matches):
    print(f"Searching matches for hero {hero}: {matches}", end="\r")


def process_hero(hero, mask, base_image):
    matches = []
    matches_count = 0

    progress(hero["name"], matches_count)

    icon, icon_h, icon_w = prepare_icon(hero["name"])

    res = cv2.matchTemplate(base_image, icon, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(res)[1]
    threshold = max(max_val - 0.05, 0.825)
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        if mask[math.ceil(pt[1] + icon_h / 2), math.ceil(pt[0] + icon_w / 2)] != 255:
            mask[pt[1] : pt[1] + icon_h, pt[0] : pt[0] + icon_w] = 255

            border_img = base_image[pt[1] + 122 : pt[1] + 128, pt[0] : pt[0] + 40]
            plus_border_img = base_image[
                pt[1] + 122 : pt[1] + 128, pt[0] - 38 : pt[0] - 30
            ]
            ascension = determine_ascension_level(border_img, plus_border_img)

            level_text_img = ip.to_ocr(
                base_image[pt[1] - 31 : pt[1], pt[0] : pt[0] + icon_w - 8]
            )

            if hero["name"] == "Wu Kong":
                level_text_img = ip.unsharp(level_text_img)

            level_text = pytesseract.image_to_string(
                level_text_img,
                config=r"--psm 7 -l digits1 --tessdata-dir ./traineddata",
            )

            level = "".join(filter(str.isdigit, level_text.split(".")[-1]))
            level = int(level) if level.isdigit() else None

            matches.append(
                {
                    "name": hero["name"],
                    "faction": hero["faction"],
                    "class": hero["class"],
                    "ascension": ascension,
                    "level": level,
                }
            )

            save_img(hero["name"], pt, level, level_text_img)
            draw_rect(base_image, pt, icon_w, icon_h)

            matches_count += 1
            progress(hero["name"], matches_count)

    print()
    return matches


def run(image_path, faction=None, class_name=None):
    clear_debug()

    heroes = load_hero_data(faction, class_name)

    base_image = prepare_image(str(consts.SCREENS_DIR / image_path))
    mask = np.zeros(base_image.shape[:2], np.uint8)

    matches = []

    for hero in heroes:
        matches.extend(process_hero(hero, mask, base_image))

    save_result(base_image)
    return matches


if __name__ == "__main__":
    data = run("smol.png")
    print(json.dumps(data))
