import math
from functools import total_ordering

import cv2
import numpy as np
import pytesseract
from pytesseract.pytesseract import Output

from . import config, debug_utils, filters, utils
from .color_tools import color_difference, get_dominant_color
from .enums import HeroAscension, Mode
from .logger import logger
from .modes import ModeSettings, get_mode_settings
from image_recognition.debug_utils import save_img

ASCENSION_COLORS = {
    HeroAscension.COMMON.value: (74, 156, 116),
    HeroAscension.RARE.value: (47, 131, 221),
    HeroAscension.ELITE.value: (134, 84, 242),
    HeroAscension.LEGENDARY.value: (252, 239, 125),
    HeroAscension.MYTHIC.value: (180, 49, 63),
    HeroAscension.ASCENDED.value: (255, 254, 255),
}


@total_ordering
class HeroCopy(object):
    def __init__(self, hero_data: dict, sections: dict, location, mode):
        self.__sections = sections

        self.mode = mode
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
        border_color = get_dominant_color(self.__sections["border"])
        ascension_ratings = {
            level: color_difference(border_color, color)
            for (level, color) in ASCENSION_COLORS.items()
        }
        ascension_level = min(ascension_ratings, key=ascension_ratings.get)

        with_plus = False
        if ascension_level not in [HeroAscension.ASCENDED, HeroAscension.COMMON]:
            border_gem_color = get_dominant_color(self.__sections["plus_border"])
            with_plus = color_difference(border_color, border_gem_color) > 28.5

        self.data["ascension"] = f"{ascension_level}{'+' if with_plus else ''}"

    def __set_stars(self):
        if self.data["ascension"] == HeroAscension.ASCENDED:
            star = cv2.imread(str(config.RESOURCES_DIR / "star.png"))
            stars_exist_confidence = cv2.minMaxLoc(
                cv2.matchTemplate(self.__sections["stars"], star, cv2.TM_CCOEFF_NORMED)
            )[1]

            # save_img(self.__sections["stars"], "stars", self.data["name"], str(stars_exist_confidence))

            if stars_exist_confidence > 0.8:
                gray = filters.to_grayscale(self.__sections["stars"])
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                thresh = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY)[1]

                num_labels, labels_im = cv2.connectedComponents(thresh)
                # save_img(labels_im, self.data["name"])
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
        if self.mode == Mode.HEROES_PAGE:
            level_text_img = filters.to_ocr(self.__sections["level"])

            level_text_img = cv2.copyMakeBorder(
                level_text_img,
                10,
                10,
                10,
                10,
                cv2.BORDER_CONSTANT,
                value=[255, 255, 255],
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
                    self.__sections["level"],
                )
        else:
            self.data["level"] = None


class Hero(object):
    def __init__(self, hero_data: dict, mode: Mode):
        self.mode = mode
        self.matches = []
        self.hero_data = utils.omit(hero_data, {"filename"})
        self.icon_img = self.__prepare_icon(hero_data["filename"])

    def create_match(self, base_img, loc):
        icon_sections = self.__split_into_sections(base_img, loc)
        match = HeroCopy(self.hero_data, icon_sections, loc, self.mode)
        self.matches.append(match)

    def __prepare_icon(self, filename: str):
        settings = get_mode_settings(self.mode, ModeSettings.HERO_ICON)

        icon_size = settings["icon_size"]
        icon_raw = cv2.imread(str(config.RESOURCES_DIR / filename))

        if settings["flip"]:
            icon_raw = cv2.flip(icon_raw, 1)

        icon = cv2.resize(icon_raw, (icon_size, icon_size))

        h_s, h_e, w_s, w_e = settings["icon_cut_ratios"]
        return icon[h_s:h_e, w_s:w_e]

    def __split_into_sections(self, base_img, loc):
        settings = get_mode_settings(self.mode, ModeSettings.SECTIONS)

        return {
            section_name: base_img[
                loc[1] + h_s : loc[1] + h_e, loc[0] + w_s : loc[0] + w_e
            ]
            for section_name, (h_s, h_e, w_s, w_e) in settings.items()
        }
