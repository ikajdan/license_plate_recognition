import argparse
import json
from pathlib import Path

from processing.logic import get_license_plate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("images_dir", type=str)
    parser.add_argument("results_file", type=str)
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    results_file = Path(args.results_file)

    images_paths = sorted(
        [
            image_path
            for image_path in images_dir.iterdir()
            if image_path.name.endswith(".jpg")
        ]
    )
    results = {}
    for image_path in images_paths:
        results[image_path.name] = get_license_plate(image_path)

    with results_file.open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=4)


if __name__ == "__main__":
    main()
