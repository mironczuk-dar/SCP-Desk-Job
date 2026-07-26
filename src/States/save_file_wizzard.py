import pygame
from datetime import datetime

from States.generic_state import GenericState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, ROOT_DIR
from Tools.text_drawing_tools import draw_text
from Tools.asset_importing_tools import import_image
from Tools.asset_scaling_tools import scale_assets_to_size
from os.path import join


class SaveFileWizzard(GenericState):

    def __init__(self, game):
        super().__init__(game)

        pygame.font.init()
        self.font_title = pygame.font.SysFont('arial', 60, bold=True)
        self.font_body = pygame.font.SysFont('arial', 28)
        self.font_small = pygame.font.SysFont('arial', 22)

        self.background = import_image(join(ROOT_DIR, 'assets', 'concept_art', 'save_file_wizzard'), format='.jpg')
        self.background = scale_assets_to_size(self.background, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.background.fill((18, 22, 35))

        self.name = ''
        self.slot_id = None

    def on_enter(self):
        self.form_data = {field: '' for field in self.fields}
        self.current_field_index = 0

    def draw(self, window):
        window.blit(self.background, (0, 0))
        

    def handling_events(self, events):
        pass

    def save_current_slot(self):
        if self.slot_id is None:
            return

        save_data = {
            'name': self.form_data.get('name', '').strip() or f'Save Slot {self.slot_id}',
            'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nights_completed': 0,
            'money': 0,
            'upgrades': [],
            'occupation': self.form_data.get('occupation', '').strip(),
            'notes': self.form_data.get('notes', '').strip(),
        }

        self.game.save_file_manager.save_slot(self.slot_id, save_data)
        self.game.state_manager.set_state('Singleplayer menu')