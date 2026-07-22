#IMPORTING LIBRARIES
from os.path import join, dirname, abspath
import pygame

#COMPUTE REPOSITORY ROOT AND GAMES DIRECTORY
ROOT_DIR = dirname(dirname(abspath(__file__)))

#IN-GAME SETTINGS
#TILE_SIZE = 8

#CONTROLLS SETTINGS
CONTROLS_DATA_PATH = join(ROOT_DIR, "data", "controls.json")
DEFAULT_CONTROLS_DATA = {
    'keyboard' : {
    'up' : pygame.K_UP,
    'down' : pygame.K_DOWN,
    'left' : pygame.K_LEFT,
    'right' : pygame.K_RIGHT,
    'options' : pygame.K_TAB,
    'action_a' : pygame.K_r,
    'action_b' : pygame.K_e,
    'action_x' : pygame.K_w,
    'action_y' : pygame.K_q
}}

#SCREEN / WINDOW SETTINGS
WINDOW_DATA_PATH = join(ROOT_DIR, 'data', 'window_data.json')
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
DEFUALT_WINDOW_DATA = {
    'width' : 1280,
    'height' : 720,
    'fullscreen' : False,
    'fps' : 60,
    'show_fps' : False,
}

#AUDIO DATA
AUDIO_DATA_PATH = join(ROOT_DIR, 'data', 'audio_data.json')
DEFAULT_AUDIO_DATA = {
    'music_on' : True,
    'sound_on' : True,
    'sound_volume' : 1,
    'music_volume' : 0.25
}

#ACHIEVEMENTS DATA
ACHIEVEMENTS_DATA_PATH = join(ROOT_DIR, 'data', 'save_data', 'achievements.json')
DEFAULT_ACHIVEMENTS_DATA = []

#SAVEFILE_DATA
#SAVEFILE_DATA_PATH = join(ROOT_DIR, 'data', 'save_data', 'save_file.json')

#GAMEFILE_DATA
GAMEFILE_DATA_PATH = join(ROOT_DIR, 'data', 'save_data', 'gamefile.json')
DEFAULT_GAMEFILE_DATA = {
    'game launched' : False,
    'Good ending unlocked' : False,
    'Bad ending unlocked' : False
}

#THEMES DATA
THEMES_DATA_PATH = join(ROOT_DIR, 'data', 'themes_data.json')
DEFAULT_THEME_DATA = {
    'current_theme' : 'Solar Flare'
}
THEME_LIBRARY = {
    'Aurora' : {'colour_1' : "#0F1B3C",
                'colour_2' : "#D7E0FF",  # Lighter, more distinct blue
                'colour_3' : "#5A7A9E",  # Mid-tone with better contrast
                'colour_4' : "#B8D0FF"},

    'Solar Flare' : {'colour_1' : "#2D1806",  # Darker base for contrast
                     'colour_2' : "#FF8F3C",  # Bright orange with better visibility
                     'colour_3' : "#CC5E2B",  # Distinct warm tone
                     'colour_4' : "#FFE4BC"}
}