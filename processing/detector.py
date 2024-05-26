import cv2
import numpy as np

import processing.config as config

def detect_license_plate(image):
    """
    Detects a license plate in an image.

    Args:
    image (numpy.ndarray): The input image.

    Returns:
    numpy.ndarray: The detected license plate.
    """

    # Extract by color
    lower_bound = np.array([0, 0, 150])
    upper_bound = np.array([180, 50, 255])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image, lower_bound, upper_bound)

    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)

        if area > config.PLATE_AREA_MIN:
            (_, (w, h), angle) = cv2.minAreaRect(contour)

            if angle > 45:
                width, height = h, w
            else:
                width, height = w, h

            if (
                config.PLATE_WIDTH_MIN < width < config.PLATE_WIDTH_MAX
                and config.PLATE_HEIGHT_MIN < height < config.PLATE_HEIGHT_MAX
            ):
                if (
                    config.PLATE_ASPECT_RATIO_MIN
                    < width / height
                    < config.PLATE_ASPECT_RATIO_MAX
                ):
                    # Approximate the contour to a polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    corners = cv2.approxPolyDP(contour, epsilon, True)

                    # Try to remove redundant corners
                    if len(corners) > 4:
                        corners = cv2.convexHull(corners)

                    # Try to approximate the contour to a rectangle
                    if len(corners) > 4:
                        epsilon = 0.025 * cv2.arcLength(contour, True)
                        corners = cv2.approxPolyDP(contour, epsilon, True)

                    if len(corners) == 4:
                        corners = sort_polygon_corners(
                            [corner[0] for corner in corners]
                        )

                        # Expand the corners to not cut off the license plate
                        corners = expand_polygon(corners, 100)

                        # Transform the license plate to a rectangle
                        src = np.float32(corners)
                        dst = np.float32(
                            [
                                [0, 0],
                                [0, config.PLATE_HEIGHT],
                                [config.PLATE_WIDTH, config.PLATE_HEIGHT],
                                [config.PLATE_WIDTH, 0],
                            ]
                        )
                        matrix = cv2.getPerspectiveTransform(src, dst)
                        license_plate = cv2.warpPerspective(
                            image, matrix, (config.PLATE_WIDTH, config.PLATE_HEIGHT)
                        )

                        # Remove space around the license plate
                        license_plate = cut_sides(license_plate, 20)

                        # Convert to grayscale
                        license_plate = cv2.cvtColor(license_plate, cv2.COLOR_HSV2BGR)
                        license_plate = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

                        # # Open
                        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        # license_plate = cv2.morphologyEx(
                        #     license_plate, cv2.MORPH_OPEN, kernel, iterations=1
                        # )

                        # # Close
                        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        # license_plate = cv2.morphologyEx(
                        #     license_plate, cv2.MORPH_CLOSE, kernel, iterations=1
                        # )

                        # # Threshold
                        # _, license_plate = cv2.threshold(
                        #     license_plate, 120, 255, cv2.THRESH_BINARY
                        # )

                        # # Dilate
                        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        # license_plate = cv2.dilate(license_plate, kernel, iterations=2)

                        # # Erode
                        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        # license_plate = cv2.erode(license_plate, kernel, iterations=2)

                        # Denoise
                        license_plate = cv2.bilateralFilter(license_plate, 15, 120, 10)

                        # Threshold
                        license_plate = cv2.adaptiveThreshold(
                            license_plate,
                            255,
                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY,
                            27,
                            1,
                        )

                        # Close
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        license_plate = cv2.morphologyEx(
                            license_plate, cv2.MORPH_CLOSE, kernel, iterations=2
                        )

                        # Dilate
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        license_plate = cv2.dilate(license_plate, kernel, iterations=1)

                        # Erode
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                        license_plate = cv2.erode(license_plate, kernel, iterations=1)

                        return license_plate
                    return None


def sort_polygon_corners(coordinates):
    """
    Sort the corners of a polygon.

    Args:
    coordinates (list): A list of coordinates representing the corners of a polygon.

    Returns:
    list: A list of coordinates sorted in a clockwise order.
    """

    sorted_by_x = sorted(coordinates, key=lambda coord: coord[0])

    bottom_half = sorted_by_x[:2]
    top_half = sorted_by_x[2:]

    bottom_half.sort(key=lambda coord: coord[1])
    top_half.sort(key=lambda coord: coord[1], reverse=True)

    sorted_coordinates = bottom_half + top_half

    return sorted_coordinates


def expand_polygon(corners, size):
    """
    Expand the corners of a polygon.

    Args:
    corners (list): A list of coordinates representing the corners of a polygon.
    size (int): The size to expand the corners by.

    Returns:
    numpy.ndarray: An array of coordinates representing the expanded corners of a polygon.
    """
    corners = np.array(corners, dtype=np.float32)
    center = np.mean(corners, axis=0)
    expanded_corners = []
    for corner in corners:
        vector = corner - center
        vector_normalized = vector / np.linalg.norm(vector)
        expanded_corner = corner + vector_normalized * size
        expanded_corners.append(expanded_corner)

    return np.array(expanded_corners, dtype=np.float32)


def cut_sides(image, x):
    """
    Cuts the left and right sides of an image by x pixels.

    Parameters:
    image (numpy.ndarray): The input image.
    x (int): The number of pixels to cut from both the left and right sides.

    Returns:
    numpy.ndarray: The cropped image.
    """
    _, width = image.shape[:2]
    x = min(x, width // 2)
    new_width = width - 2 * x
    cropped_image = image[:, x : x + new_width]

    return cropped_image
