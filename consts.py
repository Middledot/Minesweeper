"""Constants for the entire game"""

import pygame
from enum import Enum
from typing import Tuple, Union

from settingswin import SettingsWin

Coords = Tuple[Union[int, float], Union[int, float]]

# A bit hacky
# I want to create a TKinter window for settings BUT I
# inexplicably cannot do this. It will make an error that
# looks like a C traceback and stackoverflow has no
# clarification on this BUT it won't error if the window
# is created before pygame is initilialized sooo... I just
# expand and minimize a single window
tkwin = SettingsWin()
pygame.init()

segfont = pygame.font.Font("assets/DSEG14Modern-Bold.ttf", 20)

flagico = pygame.image.load("assets/flag.png")
mineico = pygame.image.load("assets/mine.png")
xico = pygame.image.load("assets/cross.png")

numtocol = {
    1: "#0000ff",
    2: "#008200",
    3: "#fe0100",
    4: "#000084",
    5: "#840000",
    6: "#008284",
    7: "#840085",
    8: "#757575"
}
FPS = 40  # Frames per second

# just state instead of GameState for simplicity
class State(Enum):
    startscreen = 0
    playing = 1
    lost = 2
    won = 3
