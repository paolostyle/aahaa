import cv2
import numpy as np

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


def gauss_diff(image):
    return cv2.GaussianBlur(image, (3, 3), 0) - cv2.GaussianBlur(image, (7, 7), 0)


def sharpen(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)


def unsharp(image):
    im = cv2.GaussianBlur(image, (0, 0), 3)
    return cv2.addWeighted(image, 5, im, -0.5, 0)


def to_ocr(image):
    return ~get_grayscale(remove_noise(sharpen(image)))

