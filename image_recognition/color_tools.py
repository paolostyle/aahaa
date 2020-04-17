import cv2
import numpy as np
from skimage.color import deltaE_cie76, rgb2lab

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
