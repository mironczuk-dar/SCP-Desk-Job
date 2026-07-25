import pygame
from datetime import datetime

from States.generic_state import GenericState
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from Tools.text_drawing_tools import draw_text


class SaveFileWizzard(GenericState):

    def __init__(self, game):
        super().__init__(game)

        pygame.font.init()
        self.font_title = pygame.font.SysFont('arial', 60, bold=True)
        self.font_body = pygame.font.SysFont('arial', 28)
        self.font_small = pygame.font.SysFont('arial', 22)

        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.fill((18, 22, 35))

        self.fields = ['name', 'occupation', 'notes']
        self.field_labels = {
            'name': 'Full Name',
            'occupation': 'Role / Occupation',
            'notes': 'Short Bio'
        }
        self.form_data = {field: '' for field in self.fields}
        self.current_field_index = 0
        self.slot_id = None

    def on_enter(self):
        self.form_data = {field: '' for field in self.fields}
        self.current_field_index = 0

    def draw(self, window):
        window.blit(self.background, (0, 0))
        draw_text(window, 'CREATE SAVE FILE', WINDOW_WIDTH // 2, 60, self.font_title)

        draw_text(window, 'Fill in your character details and press Enter to save.', WINDOW_WIDTH // 2, 140, self.font_small)

        if self.slot_id is not None:
            draw_text(window, f'Save Slot {self.slot_id}', WINDOW_WIDTH // 2, 190, self.font_small)

        start_y = 260
        for index, field in enumerate(self.fields):
            label = self.field_labels[field]
            value = self.form_data[field]
            is_active = index == self.current_field_index

            color = (255, 255, 255) if is_active else (180, 180, 180)
            draw_text(window, label, 220, start_y + index * 130, self.font_body, colour=color)

            box_rect = pygame.Rect(220, start_y + index * 130 + 40, 900, 60)
            pygame.draw.rect(window, (255, 255, 255), box_rect, 2)
            pygame.draw.rect(window, (255, 255, 255, 40), box_rect, 0)

            placeholder = value if value else f'Enter {label.lower()}...'
            text_surface = self.font_small.render(placeholder, True, (255, 255, 255))
            window.blit(text_surface, (box_rect.x + 20, box_rect.y + 15))

        hint = 'Press Enter to continue, Tab to switch fields, Escape to cancel.'
        draw_text(window, hint, WINDOW_WIDTH // 2, 760, self.font_small)

    def handling_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.game.state_manager.set_state('Singleplayer menu')
                return

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.current_field_index < len(self.fields) - 1:
                    self.current_field_index += 1
                else:
                    self.save_current_slot()
                return

            if event.key == pygame.K_TAB:
                self.current_field_index = (self.current_field_index + 1) % len(self.fields)
                return

            if event.key == pygame.K_BACKSPACE:
                field = self.fields[self.current_field_index]
                self.form_data[field] = self.form_data[field][:-1]
                return

            if event.unicode and event.unicode.isprintable():
                field = self.fields[self.current_field_index]
                self.form_data[field] += event.unicode

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