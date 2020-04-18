import math
from functools import total_ordering

import cv2
import numpy as np
import pytesseract
from pytesseract.pytesseract import Output

from . import config, debug_utils, filters, utils
from .color_tools import color_difference, get_dominant_color
from .enums import HeroAscension
from .logger import logger

ASCENSION_COLORS = {
    HeroAscension.COMMON.value: (74, 156, 116),
    HeroAscension.RARE.value: (47, 131, 221),
    HeroAscension.ELITE.value: (134, 84, 242),
    HeroAscension.LEGENDARY.value: (252, 239, 125),
    HeroAscension.MYTHIC.value: (180, 49, 63),
    HeroAscension.ASCENDED.value: (255, 254, 255),
}


class HeroIconSections(object):
    def __init__(self, loc, base_img):
        self.border = base_img[loc[1] + 122 : loc[1] + 128, loc[0] : loc[0] + 40]
        self.plus_border = base_img[
            loc[1] + 122 : loc[1] + 128, loc[0] - 38 : loc[0] - 30
        ]
        self.stars = base_img[loc[1] + 90 : loc[1] + 119, loc[0] - 46 : loc[0] + 80]
        self.level = base_img[loc[1] - 29 : loc[1], loc[0] + 1 : loc[0] + 94]


@total_ordering
class HeroCopy(object):
    def __init__(self, hero_data: dict, sections: HeroIconSections, location):
        self.__sections = sections

        self.data = hero_data.copy()
        self.location = [int(val) for val in location]

        self.__set_ascension_level()
        self.__set_stars()
        self.__set_level()

    def asdict(self):
        return self.data

    def __eq__(self, other):
        return self.location == other.location and self.data == other.data

    def __lt__(self, other):
        same_row = abs(self.location[1] - other.location[1]) < 5
        if same_row:
            return self.location[0] < other.location[0]
        else:
            return self.location[1] < other.location[1]

    def __set_ascension_level(self):
        border_color = get_dominant_color(self.__sections.border)
        ascension_ratings = {
            level: color_difference(border_color, color)
            for (level, color) in ASCENSION_COLORS.items()
        }
        ascension_level = min(ascension_ratings, key=ascension_ratings.get)

        with_plus = False
        if ascension_level not in [
            HeroAscension.ASCENDED.value,
            HeroAscension.COMMON.value,
        ]:
            border_gem_color = get_dominant_color(self.__sections.plus_border)
            with_plus = color_difference(border_color, border_gem_color) > 28.5

        self.data["ascension"] = f"{ascension_level}{'+' if with_plus else ''}"

    def __set_stars(self):
        if self.data["ascension"] == HeroAscension.ASCENDED.value:
            star = cv2.imread(str(config.RESOURCES_DIR / "star.png"))
            stars_exist_confidence = cv2.minMaxLoc(
                cv2.matchTemplate(self.__sections.stars, star, cv2.TM_CCOEFF_NORMED)
            )[1]

            if stars_exist_confidence > 0.8:
                gray = filters.to_grayscale(self.__sections.stars)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                thresh = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY)[1]

                num_labels, labels_im = cv2.connectedComponents(thresh)
                occurences = [
                    occ
                    for label, occ in zip(*np.unique(labels_im, return_counts=True))
                    if occ > 210 and occ < 290
                ]

                self.data["stars"] = len(occurences)
            else:
                self.data["stars"] = 0
        else:
            self.data["stars"] = None

    def __set_level(self):
        level_text_img = filters.to_ocr(self.__sections.level)

        level_text_img = cv2.copyMakeBorder(
            level_text_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )

        level_text = pytesseract.image_to_string(level_text_img, config=rf"--psm 7")

        level = "".join(filter(str.isdigit, level_text.split(".")[-1]))
        level = int(level) if level.isdigit() else 0

        self.data["level"] = level if (level >= 1 and level <= 500) else None

        if self.data["level"] == None:
            err_id = utils.random_str()
            logger.warn(
                f"Could not recognize level for hero {self.data['name']}, raw value: {level_text}, id: {err_id}"
            )
            debug_utils.save_img(
                self.data["name"], f"{self.location}_{err_id}_ocr", level_text_img,
            )
            debug_utils.save_img(
                self.data["name"],
                f"{self.location}_{err_id}_orig",
                self.__sections.level,
            )


class Hero(object):
    def __init__(self, hero_data: dict):
        self.matches = []
        self.__hero_data = hero_data
        self.__prepare_icon(hero_data["filename"])

    def create_match(self, icon_sections: HeroIconSections, location):
        hero_data = utils.omit(self.__hero_data, {"filename"})
        match = HeroCopy(hero_data, icon_sections, location)
        self.matches.append(match)

    def __prepare_icon(self, filename: str):
        icon_size = 151
        icon_raw = cv2.imread(str(config.RESOURCES_DIR / filename))

        icon = cv2.resize(icon_raw, (icon_size, icon_size))

        h_s = math.ceil(0.2 * icon_size)
        h_e = math.ceil(0.78 * icon_size)
        w_s = math.ceil(0.3 * icon_size)
        w_e = math.ceil(1 * icon_size)

        self.icon_img = icon[h_s:h_e, w_s:w_e]
