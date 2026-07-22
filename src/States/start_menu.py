# IMPORTING LIBRARIES
import pygame
import sys
from random import choice
from os.path import join

#IMPORTING FILES
from States.generic_state import GenericState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, ROOT_DIR

#IMPORTING ELEMENTS
from UI_elements.Generic_UI_elements.buttons import ImageAudioButton
from UI_elements.Generic_UI_elements.edited_text import create_text_with_outline

#IMPORTING AUDIO MANAGER
from Managers.audio_manager import AudioManager


#STARTER MENU CLASS
class StartMenu(GenericState):
    def __init__(s, game):
        super().__init__(game)

        # UI
        s.background = None
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

        s.setup()

    #METHOD THAT RUNS EVERY TIME WE ENTER THE MENU
    def on_enter(s):

        try:
            s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.background.fill('#ADD8E6')
            
            for btn in s.buttons:
                if hasattr(btn, 'waiting_for_audio'):
                    btn.waiting_for_audio = False
                    btn.sound = None
            
        except Exception as e:
            print(f"Error in StartMenu.on_enter: {e}")
            s.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            s.background.fill("#FF0000")

    #METHOD FOR UPDATING THE MENU (ANIMATIONS, BUTTONS, ...)
    def update(s, delta_time):

        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)
            button.update(delta_time)


    #METHOD FOR HANDLING EVENTS IN THE MENU (BUTTON CLICKS, ...)
    def handling_events(s, events):
        mouse_pos = s.game.get_scaled_mouse_pos()
        input_manager = s.game.input_manager

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

        # SYNCHRONIZACJA SELECTED
        for i, button in enumerate(s.buttons):
            button.is_selected = (i == s.active_index)

        # przekazanie eventów do przycisków
        for button in s.buttons:
            button.handling_events(events)

    #METHOD FOR DRAWING THE START MENU
    def draw(s, window):
        if s.background:
            window.blit(s.background, (0, 0))

        window.blit(s.version_surface, (
            WINDOW_WIDTH - s.version_surface.get_width() - 10,
            WINDOW_HEIGHT - s.version_surface.get_height() - 10
        ))

        for button in s.buttons:
            button.draw(window)

    #METHOD FOR SETTING UP THE MENU (CREATING BUTTONS, ...)
    def setup(s):
        button_width = 450
        pos_x = button_width // 2 + 50 
        pos_y = 80
        visible_states = ["Singleplayer menu", "Extras menu", "Options menu"]
        
        #button_image = pygame.image.load(join(ROOT_DIR, 'assets', 'images', 'button.png')).convert_alpha()
        #hovered_button_image = pygame.image.load(join(ROOT_DIR, 'assets', 'images', 'button_hovered.png')).convert_alpha()
        button_image = pygame.Surface((button_width, 60), pygame.SRCALPHA)
        button_image.fill((255, 255, 255, 200))
        hovered_button_image = pygame.Surface((button_width, 60), pygame.SRCALPHA)
        hovered_button_image.fill((0, 0, 0, 200))


        scale_ratio = button_width / button_image.get_width()
        button_image = pygame.transform.scale_by(button_image, scale_ratio)
        hovered_button_image = pygame.transform.scale_by(hovered_button_image, scale_ratio)

        for key in visible_states:
            btn = ImageAudioButton(
                s.game,
                (pos_x, pos_y),
                button_image,
                hovered_button_image,
                text=key.replace("menu", "").strip(),
                action=lambda k=key: s.game.state_manager.set_state(k),
                sound=None,
                text_size=50,
                font=None
            )
            s.buttons.append(btn)
            pos_y += button_image.get_height() + 10

        s.buttons.append(ImageAudioButton(
                s.game,
                (pos_x, pos_y),
                button_image,
                hovered_button_image,
                text="Exit Game",
                action=s.exit_game,
                sound=None,
                text_size=50,
                font=None))

    def exit_game(s):
        s.game.save()
        pygame.quit()
        sys.exit()