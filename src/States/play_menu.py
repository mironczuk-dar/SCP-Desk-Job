#IMPORTING LIBRARIES
import pygame
from os.path import join

#IMPORTING TOOLS
from Tools.asset_importing_tools import import_image
from Tools.asset_scaling_tools import scale_assets_to_size
from Tools.text_drawing_tools import draw_text

#IMPORTING FILES
from settings import ROOT_DIR, WINDOW_WIDTH, WINDOW_HEIGHT
from States.generic_state import GenericState
from Managers.save_file_manager import SaveFileManager

#IMPORTING UI ELEMENTS
from UI_elements.Play_menu_UI_elements.lockers import Locker, EmptyLocker
from UI_elements.Generic_UI_elements.buttons import GenericButton


class SingleplayerMenu(GenericState):

    def __init__(s, game):
        s.game = game
        s.save_file_manager = SaveFileManager(game)

        s.background = import_image(join(ROOT_DIR, 'assets', 'concept_art', 'Concept art 3'), format='.jpg')
        s.background = scale_assets_to_size(s.background, WINDOW_WIDTH, WINDOW_HEIGHT)

        s.font_title = pygame.font.SysFont('arial', 60, bold=True)
        
        s.back_button = GenericButton(
            game,
            (150, 50),
            (100, 50),
            "BACK",
            text_size=24,
            text_colour=(255, 255, 255),
            colour=(100, 100, 100),
            action=lambda: s.game.state_manager.set_state('Start menu')
        )

        s.lockers = []
        s.nav_elements = []
        s.current_focus_index = 0
        s.using_mouse = True

        s.setup()

    def setup(s):
        s.refresh_lockers()

    def on_enter(s):
        s.refresh_lockers()
        s.current_focus_index = 0

    def refresh_lockers(s):
        slot_data_list = s.save_file_manager.refresh_slots()
        s.lockers.clear()
        s.nav_elements = [s.back_button]

        w, h = WINDOW_WIDTH * 0.28, WINDOW_HEIGHT * 0.8
        y = WINDOW_HEIGHT * 0.1
        positions = [
            (WINDOW_WIDTH * 0.05, y),
            (WINDOW_WIDTH * 0.35, y),
            (WINDOW_WIDTH * 0.65, y),
        ]

        for data_dict, (x, y_pos) in zip(slot_data_list, positions):
            rect = pygame.Rect(x, y_pos, w, h)
            
            if data_dict['is_empty']:
                new_locker = EmptyLocker(s.game, data_dict['slot_id'], rect)
            else:
                new_locker = Locker(s.game, data_dict['slot_id'], rect, data_dict['data'])
                
            s.lockers.append(new_locker)
            s.nav_elements.append(new_locker)

    def draw(s, window):
        window.blit(s.background, (0, 0))
        draw_text(window, 'SELECT SAVE FILE', WINDOW_WIDTH // 2, 50, s.font_title)

        s.back_button.draw(window)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for locker in s.lockers:
            locker.draw(window, overlay)
        window.blit(overlay, (0, 0))

    def update(s, delta_time):
        mouse_pos = s.game.get_scaled_mouse_pos()
        input_manager = s.game.input_manager
        
        mouse_moved = pygame.mouse.get_rel() != (0, 0)
        if mouse_moved:
            s.using_mouse = True

        if input_manager.just_pressed('left') or input_manager.just_pressed('right'):
            s.using_mouse = False

        if not s.using_mouse:
            if input_manager.just_pressed('right'):
                s.current_focus_index = (s.current_focus_index + 1) % len(s.nav_elements)
            elif input_manager.just_pressed('left'):
                s.current_focus_index = (s.current_focus_index - 1) % len(s.nav_elements)
                
            for i, element in enumerate(s.nav_elements):
                element.is_hovered = (i == s.current_focus_index)
        else:
            s.back_button.update(delta_time)
            for i, element in enumerate(s.nav_elements):
                if hasattr(element, 'rect') and element.rect.collidepoint(mouse_pos):
                    element.is_hovered = True
                    s.current_focus_index = i
                else:
                    element.is_hovered = False

            for locker in s.lockers:
                locker.update(mouse_pos, delta_time)

    def handling_events(s, events):
        s.back_button.handling_events(events)
        for locker in s.lockers:
            locker.handling_events(events)

        input_manager = s.game.input_manager

        # --- 1. KEYBOARD / GAMEPAD SELECTION LOGIC ---
        if input_manager.just_pressed('accept'):
            focused_element = s.nav_elements[s.current_focus_index]
            
            if focused_element == s.back_button:
                s.back_button.action()
                
            elif isinstance(focused_element, EmptyLocker):
                # Transition to SaveFileWizzard for empty slots
                wizard_state = s.game.state_manager.states.get('Save file wizzard')
                if wizard_state is not None:
                    wizard_state.slot_id = focused_element.slot_id
                    wizard_state.on_enter()
                    s.game.state_manager.set_state('Save file wizzard')
                else:
                    print("Error: 'Save file wizzard' state not found in StateManager.")
                    
            elif isinstance(focused_element, Locker):
                focused_element.play_button.action()

        # --- 2. KEYBOARD / GAMEPAD DELETE LOGIC ---
        if input_manager.just_pressed('delete_action'):
            focused_element = s.nav_elements[s.current_focus_index]
            if isinstance(focused_element, Locker):
                focused_element.delete_button.action()
                s.refresh_lockers()

        # --- 3. MOUSE CLICK LOGIC ---
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for locker in s.lockers:
                    if locker.is_hovered:
                        if locker.is_empty:
                            # Transition to SaveFileWizzard on mouse click
                            wizard_state = s.game.state_manager.states.get('Save file wizzard')
                            if wizard_state is not None:
                                wizard_state.slot_id = locker.slot_id
                                wizard_state.on_enter()
                                s.game.state_manager.set_state('Save file wizzard')
                            else:
                                print("Error: 'Save file wizzard' state not found in StateManager.")
                        # Active lockers handle their own internal play/delete buttons via locker.handling_events()
                
                # Refresh lockers in case a delete button was clicked
                s.refresh_lockers()