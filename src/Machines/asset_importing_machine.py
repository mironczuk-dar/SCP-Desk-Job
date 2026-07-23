#IMPORTING LIBRARIES
import pygame
from pygame import mixer
from pytmx.util_pygame import load_pygame
from os.path import join

#IMPORTING TOOLS
from Tools.asset_importing_tools import *
from Tools.asset_scaling_tools import *

#IMPORTING FILES
from settings import ROOT_DIR


def load_audio(game):
    mixer.init()

    game.music_tracks = {
        'Start menu' : join(ROOT_DIR, 'audio', 'Music', 'start_menu_music.ogg'),
    }

#LOADING LEVEL ASSETS
def load_menu_assets(game):
    game.button_images = import_folder_dict(join(ROOT_DIR, 'assets', 'button_assets'))
    game.button_images = scale_asset(game.button_images, 10)

def load_game_assets(game):
    pass

#LOADING GAME FONTS
def load_fonts(game):
    pass