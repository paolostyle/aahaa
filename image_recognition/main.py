import argparse
import json
import numpy as np
from tools import (
    image_processing as ip,
    ascension_detection as ad,
    hero_recognition as hr,
    consts,
)


def progress(hero, matches):
    print(f"Searching matches for hero {hero}: {matches}", end="\r")


def process_hero(hero, mask, base_image):
    matches = []
    matches_count = 0

    progress(hero["name"], matches_count)

    hero_locations = hr.find_hero(base_image, hero["filename"])

    for pt in hero_locations:
        if hr.not_in_mask(mask, pt):
            hr.mark_mask(mask, pt)
            get_section = hr.get_icon_sections(pt, base_image)

            ascension = ad.determine_ascension_level(
                get_section("border"), get_section("plus_border")
            )
            ascension_level = None

            if ascension == "ascended":
                ascension_level = ad.get_ascension_level(get_section("stars"))

            level = ad.get_level(get_section("level"), hero["name"])

            matches.append(
                {
                    "name": hero["name"],
                    "faction": hero["faction"],
                    "class": hero["class"],
                    "rarity": hero["rarity"],
                    "ascension": ascension,
                    "ascensionLevel": ascension_level,
                    "level": level,
                }
            )

            matches_count += 1
            progress(hero["name"], matches_count)

    print()
    return matches


def recognize_heroes(image_path, faction=None, class_name=None, include_common=None):
    heroes = hr.load_hero_data(faction, class_name, include_common)
    base_image = hr.prepare_image(str(consts.SCREENS_DIR / image_path))
    mask = np.zeros(base_image.shape[:2], np.uint8)
    matches = []

    for hero in heroes:
        matches.extend(process_hero(hero, mask, base_image))

    return sorted(
        matches,
        key=lambda i: (
            -i["level"] if i["level"] is not None else 0,
            -ad.ASCENSION_COLORS_WEIGHTS[i["ascension"]],
            -i["ascensionLevel"] if i["ascensionLevel"] is not None else 0,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFK Arena heroes recognition")
    parser.add_argument("img", help="screenshot filename in screens folder")
    parser.add_argument(
        "--faction",
        help="filter search to specific faction",
        choices=consts.ALL_FACTIONS,
    )
    parser.add_argument(
        "--class",
        help="filter search to specific class",
        dest="class_name",
        choices=consts.ALL_CLASSES,
    )
    parser.add_argument(
        "--include-common",
        help="include Common heroes in the search",
        dest="include_common",
        action="store_true",
    )
    args = parser.parse_args()

    data = recognize_heroes(
        args.img, args.faction, args.class_name, args.include_common
    )
    print(json.dumps(data))
