import os
from glob import glob
from pathlib import Path

import cv2

from . import config


def clear_debug_dir():
    files = glob(str(config.DEBUG_DIR / "*"))
    for f in files:
        os.remove(f)


def draw_rect(base_image, pt, icon_w, icon_h):
    cv2.rectangle(base_image, pt, (pt[0] + icon_w, pt[1] + icon_h), (0, 0, 255), 3)


def save_img(name, details, img):
    cv2.imwrite(str(config.DEBUG_DIR / f"{name}_{details}.png"), img)


def save_result(image):
    cv2.imwrite(str(config.DEBUG_DIR / "result.png"), image)


def show_img(image):
    cv2.imshow("debug", image)
    cv2.waitKey(0)
