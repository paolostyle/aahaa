import cv2
import json
import math
import numpy as np
import pytesseract
from tools import image_processing as ip, consts
from tools.hero_recognition import prepare_icon, prepare_image, load_hero_data
from tools.debug_utils import clear_debug, draw_rect, save_level_text, save_result


def progress(hero, matches):
    print(f"Searching matches for hero {hero}: {matches}", end='\r')


def process_hero(hero, mask, base_image):
    hero["matches"] = 0
    hero["levels"] = []

    progress(hero["name"], hero["matches"])

    icon, icon_h, icon_w = prepare_icon(hero["name"])

    res = cv2.matchTemplate(base_image, icon, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(res)[1]
    threshold = max(max_val - 0.03, 0.825)
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        if mask[math.ceil(pt[1] + icon_h / 2), math.ceil(pt[0] + icon_w / 2)] != 255:
            mask[pt[1] : pt[1] + icon_h, pt[0] : pt[0] + icon_w] = 255
            hero["matches"] += 1

            level_text_img = ip.to_ocr(
                base_image[pt[1] - 31 : pt[1], pt[0] : pt[0] + icon_w - 8]
            )

            if hero["name"] == "Wu Kong":
                level_text_img = ip.unsharp(level_text_img)

            level_text = pytesseract.image_to_string(
                level_text_img,
                config=r"--psm 7 -l digits1 --tessdata-dir ./traineddata",
            )

            level = level_text.split(".")[-1]
            if level.isdigit():
                hero["levels"].append(int(level))
            else:
                hero["levels"].append(None)

            save_level_text(hero["name"], pt, level, level_text_img)
            draw_rect(base_image, pt, icon_w, icon_h)
            progress(hero["name"], hero["matches"])

    print()


def run(image_path):
    clear_debug()

    heroes = load_hero_data()

    base_image = prepare_image(str(consts.SCREENS_DIR / image_path))
    mask = np.zeros(base_image.shape[:2], np.uint8)

    for hero in heroes:
        process_hero(hero, mask, base_image)

    heroes = [hero for hero in heroes if hero["matches"] > 0]
    save_result(base_image)
    return heroes


if __name__ == "__main__":
    data = run("screen.jpg")
    print(json.dumps(data))
