import cv2
import numpy as np


def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image, blur=3):
    return cv2.medianBlur(image, blur)


def thresholding(image, thresh=0):
    return cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


def to_ocr(image):
    norm_img = cv2.normalize(
        to_grayscale(remove_noise(image)),
        None,
        alpha=0,
        beta=255,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_8UC1,
    )
    return thresholding(norm_img, 150)
