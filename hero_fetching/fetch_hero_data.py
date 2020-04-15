import json
import os
import requests
import shutil
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.request import urlretrieve

MODULE_DIR = Path(__file__).absolute().parent
RESOURCES_DIR = MODULE_DIR / "../resources"
OVERRIDES_DIR = RESOURCES_DIR / "overrides"
HERO_DATA_PATH = RESOURCES_DIR / "heroData.json"


def download_image(url, filename):
    urlretrieve(url, str(RESOURCES_DIR / filename))


def copy_overrides():
    files = os.listdir(str(OVERRIDES_DIR))

    for f in files:
        shutil.copy(str(OVERRIDES_DIR / f), str(RESOURCES_DIR))


def get_resources():
    heroes_with_skins = {
        "Brutus": 1,
        # "Tasi": 1,
    }

    response = requests.get("https://afk-arena.fandom.com/wiki/Heroes")
    document = BeautifulSoup(response.content, "html.parser")

    all_rows = document.find_all("tr")
    hero_rows = [row for row in all_rows if len(row.find_all("img")) > 0]

    heroes = []
    for hero_row in hero_rows:
        name_and_title = (
            hero_row.select("td:nth-child(3)")[0].get_text().strip().split(" - ")
        )
        name = name_and_title[0]
        url = hero_row.select("td:nth-child(2) img")[0]["data-src"]
        filename = f"{name}.jpg"

        hero_data = {
            "faction": hero_row.parent.previous_sibling.previous_sibling.find("span")[
                "id"
            ],
            "rarity": hero_row.select("td:nth-child(1)")[0].get_text().strip(),
            "class": hero_row.select("td:nth-child(4) img")[0]["alt"],
            "name": name,
            "filename": filename,
        }

        download_image(url, filename)

        if name in heroes_with_skins.keys():
            for i in range(heroes_with_skins[name]):
                if i == 0:
                    heroes.append(hero_data)
                else:
                    copy = hero_data.copy()
                    copy["filename"] = f"{name}_{i}.jpg"
                    heroes.append(copy)
        else:
            heroes.append(hero_data)

    HERO_DATA_PATH.touch()
    HERO_DATA_PATH.write_text(json.dumps(heroes))
    copy_overrides()


if __name__ == "__main__":
    get_resources()
