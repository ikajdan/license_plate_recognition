import re

import cv2
import numpy as np

import processing.config as config


def normalize_image(image):
    """
    Normalize an image.

    Args:
    image (numpy.ndarray): The image to normalize.

    Returns:
    np.ndarray: The normalized image.
    """

    height, width, _ = image.shape
    aspect_ratio = width / height
    new_height = int(config.IMAGE_WIDTH / aspect_ratio)
    image = cv2.resize(image, (config.IMAGE_WIDTH, new_height))

    return image


def validate_license_plate(plate):
    """
    Validate a Polish license plate.

    Args:
    plate (str): A string representing the license plate to be validated.

    Returns:
    bool: True if the plate is valid, False otherwise.
    """

    if len(plate) not in [7, 8]:
        return False

    pattern = r"^[A-Z]{1,2}[A-Z0-9]{4,7}$"

    return bool(re.match(pattern, plate))


def sort_polygon_corners(coordinates):
    """
    Sort the corners of a polygon in a counter-clockwise order.

    Args:
    coordinates (list): A list of coordinates representing the corners of a polygon.

    Returns:
    list: A list of coordinates sorted in a clockwise order.
    """

    # Sort the coordinates based on their x values
    sorted_by_x = sorted(coordinates, key=lambda coord: coord[0])

    # Divide the sorted list into two halves based on the y values
    bottom_half = sorted_by_x[:2]
    top_half = sorted_by_x[2:]

    # Sort each half based on their y values
    bottom_half.sort(key=lambda coord: coord[1])
    top_half.sort(key=lambda coord: coord[1], reverse=True)

    # Combine the sorted halves to get the final sorted coordinates
    sorted_coordinates = bottom_half + top_half

    return sorted_coordinates


def display_image(title, image, resize=False):
    """
    Display an image if debug mode is enabled.

    Args:
    image (numpy.ndarray): The image to display.
    title (str): The title of the window.
    resize (bool): Whether to resize the image to fit the screen.
    """

    if not config.DEBUG:
        return

    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    if resize:
        height, width, _ = image.shape
        aspect_ratio = width / height
        new_height = int(500 / aspect_ratio)
        image = cv2.resize(image, (500, new_height))

    cv2.imshow(title, image)

    while True:
        key_code = cv2.waitKey(10)
        if key_code == 27 or key_code == ord("q"):
            break

    cv2.destroyAllWindows()


def display_grid(templates, grid_size=(5, 5), template_size=(50, 50)):
    """
    Draws a grid image from a dictionary of character templates.

    Args:
    templates (dict): A dictionary where keys are character labels and values are template images.
    grid_size (tuple): The number of rows and columns in the grid.
    template_size (tuple): The size of each template image.
    """

    if not config.DEBUG:
        return

    grid_image = np.full(
        (template_size[1] * grid_size[0], template_size[0] * grid_size[1]),
        255,
        dtype=np.uint8,
    )

    idx = 0
    for row in range(grid_size[0]):
        for col in range(grid_size[1]):
            if idx < len(templates):
                template = list(templates.values())[idx]
                grid_image[
                    row * template_size[1] : (row + 1) * template_size[1],
                    col * template_size[0] : (col + 1) * template_size[0],
                ] = template
                idx += 1

    cv2.imshow("Template Grid", grid_image)

    while True:
        key_code = cv2.waitKey(10)
        if key_code == 27 or key_code == ord("q"):
            break

    cv2.destroyAllWindows()
