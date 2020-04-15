import argparse
import json
from image_recognition import recognize_heroes, HeroFaction, HeroClass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFK Arena heroes recognition")
    parser.add_argument("img", help="screenshot filename in screens folder")
    parser.add_argument(
        "--faction",
        help="filter search to specific faction",
        choices=[faction.value for faction in HeroFaction],
    )
    parser.add_argument(
        "--class",
        help="filter search to specific class",
        dest="class_name",
        choices=[hero_class.value for hero_class in HeroClass],
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
