import base64
import time

import cv2
import numpy as np


def create_file(base64_string):
    imgdata = base64.b64decode(base64_string)

    filename = "tmp/xt" + str(int(round(time.time() * 1000))) + ".png"

    with open(filename, 'wb') as f:
        f.write(imgdata)

    return filename


def remove_noise(image):
    blurred = cv2.bilateralFilter(image, 15, 75, 75)
    image = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
    image = cv2.bilateralFilter(image, 15, 75, 75)
    return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)


def findText(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    grad = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)

    _, bw = cv2.threshold(
        grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    return cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)


def remove_line(image):
    image = cv2.bitwise_not(image)
    bw = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 15, -2)

    horizontal = np.copy(bw)
    vertical = np.copy(bw)

    cols = horizontal.shape[1]
    horizontal_size = int(cols / 30)

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(
        cv2.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    horizontal_inv = cv2.bitwise_not(horizontal)

    # perform bitwise_and to mask the lines with provided mask
    image = cv2.bitwise_and(image, image, mask=horizontal_inv)

    rows = vertical.shape[0]
    verticalsize = int(rows / 30)

    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    vertical_inv = cv2.bitwise_not(vertical)

    # perform bitwise_and to mask the lines with provided mask
    image = cv2.bitwise_and(image, image, mask=vertical_inv)

    return cv2.bitwise_not(image)
