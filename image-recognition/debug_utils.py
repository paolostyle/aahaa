import cv2
from glob import glob
import os


def clear_debug():
    files = glob(r"./debug/*")
    for f in files:
        os.remove(f)


def draw_rect(base_image, pt, icon_w, icon_h):
    cv2.rectangle(base_image, pt, (pt[0] + icon_w, pt[1] + icon_h), (0, 0, 255), 3)


def save_level_text(name, pt, level, level_img):
    cv2.imwrite(f"./debug/{name}_{pt[0]}_{pt[1]}___{level}.png", level_img)
