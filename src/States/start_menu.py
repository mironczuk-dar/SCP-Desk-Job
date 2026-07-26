# IMPORTING LIBRARIES
import pygame
import sys
from random import choice
from os.path import join

# IMPORTING FILES
from States.generic_state import GenericState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, ROOT_DIR

# IMPROTING TOOLS
from Tools.asset_importing_tools import import_image
from Tools.asset_scaling_tools import scale_assets_to_size

# IMPORTING ELEMENTS
from UI_elements.Generic_UI_elements.buttons import ImageAudioButton
from UI_elements.Generic_UI_elements.edited_text import create_text_with_outline

# IMPORTING AUDIO MANAGER
from Managers.audio_manager import AudioManager


# STARTER MENU CLASS
class StartMenu(GenericState):
    def __init__(s, game):
        super().__init__(game)

        # UI
        s.background = import_image(join(ROOT_DIR, 'assets', 'concept_art', 'start_menu'), format='.jpg')
        s.background = scale_assets_to_size(s.background, WINDOW_WIDTH, WINDOW_HEIGHT)
        s.button_background = import_image(join(ROOT_DIR, 'assets', 'start_menu_assets', 'button_background'))
        s.button_background = scale_assets_to_size(s.button_background, 650, 580)
        s.font = pygame.font.SysFont(None, 40)
        s.buttons = []

        # KEYBOARD NAVIGATION
        s.active_index = 0

        # VERSION TEXT
        s.version_surface = create_text_with_outline(
            'Version: ALPHA 1.0.0',
            s.font,
            (255,255,255),
            (0,0,0),
            4
        )

        # SET SOUND NAME HERE (Make sure this matches what is loaded in your AudioManager)
        s.hover_sound_name = pygame.mixer.Sound(join(ROOT_DIR, 'audio', 'Sounds', 'start_menu_sounds', 'button_switch_sound.mp3'))

        s.setup()

    # METHOD THAT RUNS EVERY TIME WE ENTER THE MENU
    def on_enter(s):
        try:
            for btn in s.buttons:
                if hasattr(btn, 'waiting_for_audio'):
                    btn.waiting_for_audio = False
                    btn.sound = None
            
        except Exception as e:
            print(f"Error in StartMenu.on_enter: {e}")
            s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.background.fill("#FF0000")

    # METHOD FOR UPDATING THE MENU (ANIMATIONS, BUTTONS, ...)
    def update(s, delta_time):
        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)
            button.update(delta_time)

    # METHOD FOR HANDLING EVENTS IN THE MENU (BUTTON CLICKS, ...)
    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        input_manager = s.game.input_manager

        # Track the previous index to detect when a switch occurs
        previous_index = s.active_index

        if input_manager.just_pressed('up'):
            s.active_index = (s.active_index - 1) % len(s.buttons)

        elif input_manager.just_pressed('down'):
            s.active_index = (s.active_index + 1) % len(s.buttons)

        elif input_manager.just_pressed('action_a'):
            if s.buttons:
                s.buttons[s.active_index].press()

        # HOVER MYSZY
        for i, button in enumerate(s.buttons):
            if button.rect.collidepoint(mouse_pos):
                s.active_index = i

        # PLAY CLANK SOUND IF INDEX CHANGED (Hovered a new button)
        if s.active_index != previous_index:
            if hasattr(s.game, 'audio_manager'):
                s.game.audio_manager.play_sound(s.hover_sound_name)

        # SYNCHRONIZACJA SELECTED
        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)

        # przekazanie eventów do przycisków
        for button in s.buttons:
            button.handling_events(events)

    # METHOD FOR DRAWING THE START MENU
    def draw(s, window):
        if s.background:
            window.blit(s.background, (0, 0))
            window.blit(s.button_background, (0,0))

        window.blit(s.version_surface, (
            WINDOW_WIDTH - s.version_surface.get_width() - 10,
            WINDOW_HEIGHT - s.version_surface.get_height() - 10
        ))

        for button in s.buttons:
            button.draw(window)

    # METHOD FOR SETTING UP THE MENU (CREATING BUTTONS, ...)
    def setup(s):
        button_width = 550
        button_height = 120
        pos_x = button_width // 2 + 50 
        pos_y = 100
        
        buttons_dir = join(ROOT_DIR, 'assets', 'start_menu_assets', 'buttons')

        # 1. LOAD THE HOVER OUTLINE IMAGE ONCE
        try:
            outline_path = join(buttons_dir, 'hovered_outline')
            outline_img = import_image(outline_path, format='.png')
            outline_img = scale_assets_to_size(outline_img, button_width, button_height)
        except Exception as e:
            print(f"Warning: Could not load outline image ({e}). Creating blank outline.")
            outline_img = pygame.Surface((button_width, button_height), pygame.SRCALPHA)

        # Configuration tuples: (Target State Name, Display Text, Asset Filename Prefix)
        button_configs = [
            ("Play menu", "Play", "play"),
            ("Extras menu", "Extras", "extras"),
            ("Options menu", "Options", "options"),
            (None, "Exit Game", "exit")
        ]

        for state_name, display_text, prefix in button_configs:
            normal_image_path = join(buttons_dir, f"{prefix}_button")
            hover_image_path = join(buttons_dir, f"{prefix}_button_hovered")

            try:
                # Load actual assets using your import tool
                button_image = import_image(normal_image_path, format='.png')
                hovered_button_image = import_image(hover_image_path, format='.png')

                # Scale assets to fit the required button dimensions
                button_image = scale_assets_to_size(button_image, button_width, button_height)
                hovered_button_image = scale_assets_to_size(hovered_button_image, button_width, button_height)
                
                # 2. OVERLAY THE HOVER OUTLINE ONTO THE HOVERED BUTTON IMAGE
                hovered_button_image.blit(outline_img, (0, 0))

            except Exception as e:
                print(f"Warning: Could not load assets for '{prefix}' button ({e}). Using fallback surfaces.")
                button_image = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                button_image.fill((255, 255, 255, 200))
                hovered_button_image = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
                hovered_button_image.fill((0, 0, 0, 200))
                hovered_button_image.blit(outline_img, (0, 0)) # Apply outline to fallback as well

            # Set action depending on whether it switches state or exits the game
            if state_name:
                action = lambda k=state_name: s.game.state_manager.set_state(k)
            else:
                action = s.exit_game

            btn = ImageAudioButton(
                s.game,
                (pos_x, pos_y),
                button_image,
                hovered_button_image,
                text='',
                action=action,
                sound=None,
                text_size=50,
                font=None
            )
            s.buttons.append(btn)
            pos_y += button_height + 10

    def exit_game(s):
        s.game.save()
        pygame.quit()
        sys.exit()