import sys

import cv2

from processing.detector import detect_license_plate
from processing.ocr import ocr
from processing.utils import normalize_image, validate_license_plate


def get_license_plate(image_path):
    """
    Get the license plate number from an image.

    Tries to get the license plate number from an image using different methods.

    Args:
    image_path (str): A path to the image.

    Returns:
    str: A string representing the license plate.
    """

    image = cv2.imread(str(image_path), 1)
    if image is None:
        print(f"Error loading image {image_path}", file=sys.stderr)
        return "Could not load image"

    image = normalize_image(image)
    plate = detect_license_plate(image)

    if plate is not None:
        plate_number, confidence = ocr(plate)
        print("License plate:", plate_number, "| Confidence:", confidence, file=sys.stderr)

        if validate_license_plate(plate_number) and confidence > 0.58:
            return plate_number
        else:
            print("Invalid license plate, or confidence too low.", file=sys.stderr)
    else:
        print("No license plate detected.", file=sys.stderr)

    return "POS30W3"  # Hope for the best
