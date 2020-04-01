import cv2
from glob import glob
import os
from . import consts
from pathlib import Path


def clear_debug():
    files = glob(str(consts.DEBUG_DIR / "*"))
    for f in files:
        os.remove(f)


def draw_rect(base_image, pt, icon_w, icon_h):
    cv2.rectangle(base_image, pt, (pt[0] + icon_w, pt[1] + icon_h), (0, 0, 255), 3)


def save_img(name, pt, suffix, img):
    cv2.imwrite(str(consts.DEBUG_DIR / f"{name}_{pt[0]}_{pt[1]}___{suffix}.png"), img)


def save_result(image):
    cv2.imwrite(str(consts.DEBUG_DIR / "result.png"), image)


def show_img(image):
    cv2.imshow("debug", image)
    cv2.waitKey(0)
