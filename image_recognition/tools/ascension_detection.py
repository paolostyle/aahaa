import cv2
import numpy as np
import pytesseract
from skimage.color import deltaE_cie76, rgb2lab
from tools import image_processing as ip, consts

ASCENSION_COLORS = {
    "common": (74, 156, 116),
    "rare": (47, 131, 221),
    "elite": (134, 84, 242),
    "legendary": (252, 239, 125),
    "mythic": (180, 49, 63),
    "ascended": (255, 254, 255),
}

ASCENSION_COLORS_WEIGHTS = {
    "common": 0,
    "rare": 1,
    "rare+": 2,
    "elite": 3,
    "elite+": 4,
    "legendary": 5,
    "legendary+": 6,
    "mythic": 7,
    "mythic+": 8,
    "ascended": 9,
}


def determine_ascension_level(border_img, plus_border_img):
    border_color = get_dominant_color(border_img)
    ascension_ratings = {
        level: color_difference(border_color, color)
        for (level, color) in ASCENSION_COLORS.items()
    }
    ascension_level = min(ascension_ratings, key=ascension_ratings.get)

    with_plus = False
    if ascension_level not in ["ascended", "common"]:
        border_gem_color = get_dominant_color(plus_border_img)
        with_plus = color_difference(border_color, border_gem_color) > 28.5

    return f"{ascension_level}{'+' if with_plus else ''}"


def get_level(level_section, hero_name):
    level_text_img = ip.to_ocr(level_section)

    if hero_name == "Wu Kong":
        level_text_img = ip.unsharp(level_text_img)

    level_text = pytesseract.image_to_string(
        level_text_img, config=r"--psm 7 -l digits1 --tessdata-dir ./traineddata",
    )

    level = "".join(filter(str.isdigit, level_text.split(".")[-1]))
    level = int(level) if level.isdigit() else 0
    return level if (level >= 1 and level <= 500) else None


star = cv2.imread(str(consts.RESOURCES_DIR / "star.png"))


def get_ascension_level(star_section):
    stars_exist_confidence = cv2.minMaxLoc(
        cv2.matchTemplate(star_section, star, cv2.TM_CCOEFF_NORMED)
    )[1]

    if stars_exist_confidence > 0.8:
        gray = cv2.cvtColor(star_section, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY)[1]

        num_labels, labels_im = cv2.connectedComponents(thresh)
        occurences = [
            occ
            for label, occ in zip(*np.unique(labels_im, return_counts=True))
            if occ > 210 and occ < 290
        ]
        return len(occurences)
    else:
        return 0


def get_dominant_color(image):
    average = image.mean(axis=0).mean(axis=0)

    pixels = np.float32(image.reshape(-1, 3))

    n_colors = 3
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]

    return np.flip(dominant)


def color_difference(a, b):
    a_3d = np.uint8(np.asarray([[a]]))
    b_3d = np.uint8(np.asarray([[b]]))
    return deltaE_cie76(rgb2lab(a_3d), rgb2lab(b_3d)).flatten()[0]
