import os

import cv2
import numpy as np

import processing.config as config
from processing.utils import display_grid, display_image


def ocr(license_plate):
    """
    Perform OCR on a license plate image.

    Args:
    license_plate (numpy.ndarray): The license plate image.

    Returns:
    str: The license plate number.
    float: The confidence score (0.0 to 1.0).
    """

    # Segment characters
    characters = segment_characters(license_plate)
    templates = load_templates("./characters")

    display_grid(
        templates,
        grid_size=(6, 6),
        template_size=(config.OCR_CHARACTER_WIDTH, config.OCR_CHARACTER_HEIGHT),
    )

    plate_number = ""
    confidence = []

    for i, character in enumerate(characters):
        character = cv2.resize(
            character, (config.OCR_CHARACTER_WIDTH, config.OCR_CHARACTER_HEIGHT)
        )

        best_match = ""
        best_match_score = 0.0

        for char, template in templates.items():
            score = cv2.matchTemplate(character, template, cv2.TM_CCOEFF_NORMED)[0][0]
            if score > best_match_score:
                best_match = char
                best_match_score = score

        # Quirks
        if i == 0 or i == 1:
            best_match_map = {
                "0": "O",
                "1": "I",
                "2": "Z",
                "4": "A",
                "3": "E",
                "5": "S",
                "6": "G",
                "7": "T",
                "8": "B",
                "9": "P",
            }
            best_match = best_match_map.get(best_match, best_match)

        if i > 0 and plate_number[-1] == "O" and best_match == "O":
            best_match = "0"

        plate_number += best_match
        confidence.append(best_match_score)

    return plate_number, np.mean(confidence)


def load_templates(template_path):
    """
    Load character templates from the specified directory.

    Args:
    template_path (str): Path to the directory containing character templates.

    Returns:
    dict: A dictionary where keys are character labels and values are template images.
    """

    templates = {}
    for filename in os.listdir(template_path):
        if filename.endswith(".png"):
            char = os.path.splitext(filename)[0]
            template = cv2.imread(
                os.path.join(template_path, filename), cv2.IMREAD_GRAYSCALE
            )

            template = cv2.resize(
                template, (config.OCR_CHARACTER_WIDTH, config.OCR_CHARACTER_HEIGHT)
            )

            templates[char] = template

    return templates


def segment_characters(license_plate):
    """
    Segment characters from a license plate image.

    Args:
    license_plate (numpy.ndarray): The license plate image.

    Returns:
    list: A list of segmented character images.
    """

    edges = cv2.Canny(license_plate, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_contours = []
    for c in contours:
        if config.DEBUG:
            print("Contour area:", cv2.contourArea(c))
            print("Width:", cv2.boundingRect(c)[2])
            print("Height:", cv2.boundingRect(c)[3])
            img = license_plate.copy()
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            display_image("Plate Image", img, False)

        if (
            cv2.boundingRect(c)[2] > config.OCR_CHARACTER_WIDTH_MIN
            and cv2.boundingRect(c)[2] < config.OCR_CHARACTER_WIDTH_MAX
            and cv2.boundingRect(c)[3] > config.OCR_CHARACTER_HEIGHT_MIN
            and cv2.boundingRect(c)[3] < config.OCR_CHARACTER_HEIGHT_MAX
        ):
            best_contours.append(c)

    # Only keep 8 the largest contours
    best_contours = sorted(best_contours, key=cv2.contourArea, reverse=True)[:8]

    # Sort contours by x position
    best_contours = sorted(best_contours, key=lambda c: cv2.boundingRect(c)[0])

    characters = []
    for c in best_contours:
        x, y, w, h = cv2.boundingRect(c)
        character = license_plate[y : y + h, x : x + w]
        characters.append(character)

    return characters
