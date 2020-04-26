import math

import cv2
import numpy as np

from . import config
from .hero import Hero


class BaseImage(object):
    def __init__(self, filename: str):
        self.__prepare_image(str(config.SCREENS_DIR / filename))
        self.__mask = np.zeros(self.image.shape[:2], np.uint8)

    def find_hero_copies(self, hero: Hero):
        icon_size = hero.icon_img.shape[:2]
        results = cv2.matchTemplate(self.image, hero.icon_img, cv2.TM_CCOEFF_NORMED)
        max_match = cv2.minMaxLoc(results)[1]
        threshold = max(max_match - 0.05, 0.825)
        valid_results = np.where(results >= threshold)

        for location in zip(*valid_results[::-1]):
            if not self.__is_masked(location, *icon_size):
                self.__mark_mask(location, *icon_size)
                hero.create_match(self.image, location)

    def __is_masked(self, loc, icon_h, icon_w):
        height = math.ceil(loc[1] + icon_h / 2)
        width = math.ceil(loc[0] + icon_w / 2)
        return self.__mask[height, width] == 255

    def __mark_mask(self, loc, icon_h, icon_w):
        self.__mask[loc[1] : loc[1] + icon_h, loc[0] : loc[0] + icon_w] = 255

    def __prepare_image(self, file_path: str):
        original_image = cv2.imread(file_path)
        original_h, original_w = original_image.shape[:2]
        target_w = 1080
        target_h = round(target_w / original_w * original_h)

        base_image = cv2.resize(original_image, (target_w, target_h))
        base_h, base_w = base_image.shape[:2]

        top_cut = 190
        bottom_cut = 470
        self.image = base_image[top_cut : base_h - bottom_cut, :]
