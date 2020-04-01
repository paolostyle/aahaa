import cv2
import numpy as np
from skimage.color import deltaE_cie76, rgb2lab

ASCENSION_COLORS = {
    "common": (74, 156, 116),
    "rare": (47, 131, 221),
    "elite": (134, 84, 242),
    "legendary": (252, 239, 125),
    "mythic": (180, 49, 63),
    "ascended": (255, 254, 255),
}


def determine_ascension_level(border_img, plus_border_img):
    border_color = get_dominant_color(border_img)
    border_gem_color = get_dominant_color(plus_border_img)

    ascension_ratings = {
        level: color_difference(border_color, color)
        for (level, color) in ASCENSION_COLORS.items()
    }
    ascension_level = min(ascension_ratings, key=ascension_ratings.get)

    with_plus = False
    if ascension_level not in ["ascended", "common"]:
        with_plus = color_difference(border_color, border_gem_color) > 28.5

    return f"{ascension_level}{'+' if with_plus else ''}"


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
