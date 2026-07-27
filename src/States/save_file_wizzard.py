import pygame
from datetime import datetime
from os.path import join

from States.generic_state import GenericState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, ROOT_DIR
from Tools.text_drawing_tools import draw_text
from Tools.asset_importing_tools import import_image
from Tools.asset_scaling_tools import scale_assets_to_size
from UI_elements.Generic_UI_elements.buttons import ImageAudioButton

from UI_elements.Save_file_wizzard_UI_elements.embosser_device import EmbroiderTool

class SaveFileWizzard(GenericState):

    def __init__(self, game):
        super().__init__(game)

        pygame.font.init()
        self.font_title = pygame.font.SysFont('arial', 120, bold=True)
        self.font_body = pygame.font.SysFont('arial', 28)
        self.font_small = pygame.font.SysFont('arial', 22)

        self.background = import_image(join(ROOT_DIR, 'assets', 'concept_art', 'save_file_wizzard'), format='.jpg')
        self.background = scale_assets_to_size(self.background, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.name = ''
        self.slot_id = None
        
        # Position the embosser on the right side of the screen per the sketch
        embosser_x = WINDOW_WIDTH - 590
        embosser_y = 140
        self.embosser = EmbroiderTool(self.game, (embosser_x, embosser_y), 90, self.handle_key_input)

        # TRASHCAN BUTTON
        self.width = 100
        self.height = 100

        # Create placeholder surfaces explicitly
        trashcan_img = pygame.Surface((self.width, self.height))
        trashcan_img.fill((200, 0, 0))

        trashcan_hover_img = pygame.Surface((self.width, self.height))
        trashcan_hover_img.fill((255, 0, 0))

        self.trashcan = ImageAudioButton(
            game=game,
            pos=(WINDOW_WIDTH - self.width//2 - 20, self.height - 20), # added 20px padding from screen edge
            image=trashcan_img,
            hover_image=trashcan_hover_img,
            text='cancel',
            text_colour=(0, 0, 0),
            text_size=30,
            action=self.cancel_creation
        )

    def on_enter(self):
        self.name = ''

    def handle_key_input(self, key):
        """Callback fired by the EmbroiderTool whenever a key is successfully triggered."""
        if key == 'BACK':
            self.name = self.name[:-1]
        elif key == 'ENTER':
            if len(self.name.strip()) > 0:
                self.save_current_slot()
        else:
            if len(self.name) < 14:  # Restrict name length to fit the form line
                self.name += key

    def update(self, delta_time):
        self.embosser.update(delta_time)
        self.trashcan.update(delta_time)

    def draw(self, window):
        window.blit(self.background, (0, 0))
        
        # Draw the stamped text onto the clipboard form
        draw_text(window, self.name, WINDOW_WIDTH // 2, 940, self.font_title, colour=(20, 30, 45))
        
        # Draw the physical machine & button
        self.embosser.draw(window)
        self.trashcan.draw(window)

    def handling_events(self, events):
        self.embosser.handling_events(events)
        self.trashcan.handling_events(events)

    def save_current_slot(self):
        if self.slot_id is None:
            return

        save_data = {
            'name': self.name.strip() or f'Subject-{self.slot_id}',
            'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nights_completed': 0,
            'money': 0,
            'upgrades': [],
            'occupation': 'Intake Analyst',
            'notes': '',
        }

        self.game.save_file_manager.save_slot(self.slot_id, save_data)
        self.game.state_manager.set_state('Play menu')

    def cancel_creation(self):
        self.game.state_manager.set_state('Play menu')