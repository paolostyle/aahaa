from enum import Enum, auto


class AutoNameEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.replace("_PLUS", "+").capitalize()


class HeroFaction(AutoNameEnum):
    LIGHTBEARERS = auto()
    MAULERS = auto()
    WILDERS = auto()
    GRAVEBORNS = auto()
    CELESTIALS = auto()
    HYPOGEANS = auto()
    DIMENSIONALS = auto()


class HeroClass(AutoNameEnum):
    AGILITY = auto()
    INTELLIGENCE = auto()
    STRENGTH = auto()


class HeroAscension(AutoNameEnum):
    COMMON = auto()
    RARE = auto()
    RARE_PLUS = auto()
    ELITE = auto()
    ELITE_PLUS = auto()
    LEGENDARY = auto()
    LEGENDARY_PLUS = auto()
    MYTHIC = auto()
    MYTHIC_PLUS = auto()
    ASCENDED = auto()


class HeroRarity(AutoNameEnum):
    COMMON = auto()
    LEGENDARY_PLUS = auto()
    ASCENDED = auto()


class Mode(str, Enum):
    HEROES_PAGE = "heroes_page"
    CHALLENGER_LINEUP = "challenger_lineup"
