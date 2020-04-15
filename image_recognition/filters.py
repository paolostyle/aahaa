import cv2
import numpy as np

def to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    return cv2.medianBlur(image, 5)


def sharpen(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)


def unsharp(image):
    im = cv2.GaussianBlur(image, (0, 0), 3)
    return cv2.addWeighted(image, 5, im, -0.5, 0)


def to_ocr(image):
    return ~to_grayscale(remove_noise(sharpen(image)))

