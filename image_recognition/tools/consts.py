from pathlib import Path

DEBUG_DIR = Path.cwd() / '../debug'
SCREENS_DIR = Path.cwd() / '../screens'
RESOURCES_DIR = Path.cwd() / '../resources'
HERO_DATA_FILENAME = 'heroData.json'

SCREEN_WIDTH = 1080

# Factions
LIGHTBEARERS = 'Lightbearers'
MAULERS = 'Maulers'
WILDERS = 'Wilders'
GRAVEBORNS = 'Graveborns'
CELESTIALS = 'Celestials'
HYPOGEANS = 'Hypogeans'
DIMENSIONALS = 'Dimensionals'

ALL_FACTIONS = [
    LIGHTBEARERS,
    MAULERS,
    WILDERS,
    GRAVEBORNS,
    CELESTIALS,
    HYPOGEANS,
    DIMENSIONALS
]

# Classes
ALL_CLASSES = [
    'Agility',
    'Intelligence',
    'Strength'
]
