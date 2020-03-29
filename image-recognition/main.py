import cv2
import json
import numpy as np
import math
import pytesseract
from hero_recognition import prepare_icon, prepare_image, load_hero_data
import image_preprocessing as ip
from debug_utils import clear_debug, draw_rect, save_level_text

clear_debug()

heroes = load_hero_data()
base_image, base_h, base_w = prepare_image("screens/rand.png")
mask = np.zeros((base_h, base_w), np.uint8)

for hero in heroes:
    icon, icon_h, icon_w = prepare_icon(hero["name"], base_w)
    res = cv2.matchTemplate(base_image, icon, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(res)[1]
    print(hero["name"], max_val)
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

            # save_level_text(hero["name"], pt, level, level_text_img)
            # draw_rect(base_image, pt, icon_w, icon_h)

heroes = [hero for hero in heroes if hero["matches"] > 0]
print("\n\n")
print(json.dumps(heroes))

# cv2.imwrite("result.png", base_image)
