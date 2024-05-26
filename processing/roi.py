import cv2
import numpy as np

import processing.config as config


def get_roi(image):
    """
    Extract the region of interest from an image.

    Args:
    image (np.ndarray): An image in which to detect the license plate.

    Returns:
    np.ndarray: The region of interest.
    """

    roi = image.copy()

    # Blur
    image = cv2.medianBlur(image, 9)

    # Extract by color
    lower_bound = np.array([75, 130, 100])
    upper_bound = np.array([140, 240, 220])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image, lower_bound, upper_bound)
    image = cv2.bitwise_and(image, image, mask=mask)

    # Convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Erode and Dilate
    image = cv2.erode(image, np.ones((3, 3), np.uint8), iterations=1)
    image = cv2.dilate(image, np.ones((3, 3), np.uint8), iterations=1)

    # Threshold
    _, image = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)

    # Detect edges
    edges = cv2.Canny(image, 80, 250)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours
    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        _, _, w, h = cv2.boundingRect(contour)
        ratio = w / h

        # Filter by area
        if area < 5 or area > 71424:
            continue

        # Filter by aspect ratio
        if ratio < 0.2 or ratio > 0.8:
            continue

        valid_contours.append(contour)

    if valid_contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        x, y, _, h = cv2.boundingRect(contours[0])
        start_x = max(x - int(config.IMAGE_WIDTH / 100), 0)

        padding = 1000
        start_y = max(y - padding, 0)
        end_y = min(y + h + padding, roi.shape[0])

        roi = roi[start_y:end_y, start_x:]

    return roi
