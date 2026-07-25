import pygame
from UI_elements.Generic_UI_elements.buttons import GenericButton

class GenericLocker:
    def __init__(s, game, slot_id, rect):
        s.game = game
        s.slot_id = slot_id
        s.rect = rect
        s.is_hovered = False
        s.is_empty = True

        s.font_title = pygame.font.SysFont('arial', 36, bold=True)
        s.font_body = pygame.font.SysFont('arial', 24)
        s.font_small = pygame.font.SysFont('arial', 18)

    def draw(s, window, overlay):
        pass

    def update(s, mouse_pos, delta_time):
        s.is_hovered = s.rect.collidepoint(mouse_pos)

    def _draw_text(s, surface, text, font, color, x, y):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        surface.blit(text_surf, text_rect)

    def handling_events(s, events):
        pass


class EmptyLocker(GenericLocker):
    def __init__(self, game, slot_id, rect):
        super().__init__(game, slot_id, rect)

        self.is_empty = True

        self.font_header = pygame.font.SysFont("arial", 20, bold=True)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_body = pygame.font.SysFont("arial", 22)
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_plus = pygame.font.SysFont("arial", 96, bold=True)

    def update(self, mouse_pos, delta_time):
        pass  # Handled by SingleplayerMenu focus logic

    def draw(self, window, overlay):
        bg = (30, 33, 40)
        header = (42, 46, 56)
        border = (70, 85, 105)

        if self.is_hovered:
            border = (110, 185, 255)
            glow = pygame.Surface(
                (self.rect.w + 16, self.rect.h + 16),
                pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow,
                (110, 185, 255, 35),
                glow.get_rect(),
                border_radius=18
            )
            window.blit(glow, (self.rect.x - 8, self.rect.y - 8))

        pygame.draw.rect(window, bg, self.rect, border_radius=14)
        pygame.draw.rect(window, border, self.rect, width=3, border_radius=14)

        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 55)
        pygame.draw.rect(window, header, header_rect, border_top_left_radius=14, border_top_right_radius=14)

        title = self.font_header.render(f"SAVE SLOT {self.slot_id}", True, (255, 255, 255))
        window.blit(title, (self.rect.x + 18, self.rect.y + 16))

        status = self.font_small.render("EMPTY", True, (170, 170, 170))
        window.blit(status, (self.rect.right - status.get_width() - 18, self.rect.y + 18))

        plus_colour = (70, 150, 255)
        if self.is_hovered:
            plus_colour = (120, 210, 255)

        plus = self.font_plus.render("+", True, plus_colour)
        plus_rect = plus.get_rect(center=(self.rect.centerx, self.rect.y + 145))
        window.blit(plus, plus_rect)

        title_surf = self.font_title.render("Empty Save Slot", True, (245, 245, 245))
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 245))
        window.blit(title_surf, title_rect)

        subtitle = self.font_body.render("Start a New Adventure", True, (165, 170, 180))
        subtitle_rect = subtitle.get_rect(center=(self.rect.centerx, self.rect.y + 285))
        window.blit(subtitle, subtitle_rect)

        hint = "Click to begin" if self.is_hovered else "Click to create a new save"
        hint_surface = self.font_small.render(hint, True, (130, 135, 145))
        hint_rect = hint_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 35))
        window.blit(hint_surface, hint_rect)

    def handling_events(s, events):
        pass



class Locker(GenericLocker):
    def __init__(self, game, slot_id, rect, data):
        super().__init__(game, slot_id, rect)

        self.is_empty = False
        self.data = data

        self.font_header = pygame.font.SysFont("arial", 20, bold=True)
        self.font_title = pygame.font.SysFont("arial", 30, bold=True)
        self.font_label = pygame.font.SysFont("arial", 18)
        self.font_body = pygame.font.SysFont("arial", 22)
        self.font_small = pygame.font.SysFont("arial", 16)

        self.padding = 22

        # --- Side-by-side button layout ---
        button_w = 115
        button_h = 38
        spacing = 12
        button_y = rect.bottom - 28

        play_x = rect.centerx - (button_w // 2) - (spacing // 2)
        delete_x = rect.centerx + (button_w // 2) + (spacing // 2)

        self.play_button = GenericButton(
            game,
            (button_w, button_h),
            (play_x, button_y),
            "PLAY",
            text_size=20,
            text_colour=(255, 255, 255),
            colour=(46, 139, 87),  # Green
            action=lambda: print(f"Loading save {data.get('name')} from slot {slot_id}")
        )

        self.delete_button = GenericButton(
            game,
            (button_w, button_h),
            (delete_x, button_y),
            "DELETE",
            text_size=20,
            text_colour=(255, 255, 255),
            colour=(175, 45, 45),  # Red
            action=lambda: game.save_file_manager.delete_slot(slot_id)
        )

    def update(self, mouse_pos, delta_time):
        if self.is_hovered:
            self.play_button.update(delta_time)
            self.delete_button.update(delta_time)

    def handling_events(self, events):
        if self.is_hovered:
            self.play_button.handling_events(events)
            self.delete_button.handling_events(events)

    def _label(self, surface, text, x, y):
        img = self.font_label.render(text, True, (145, 150, 165))
        surface.blit(img, (x, y))

    def _value(self, surface, text, x, y):
        img = self.font_body.render(str(text), True, (240, 240, 240))
        surface.blit(img, (x, y))

    def _divider(self, surface, y):
        pygame.draw.line(surface, (65, 70, 82), (self.rect.x + 20, y), (self.rect.right - 20, y), 2)

    def _progress_bar(self, surface, x, y, width, value):
        pygame.draw.rect(surface, (55, 58, 66), (x, y, width, 12), border_radius=6)
        fill = int(width * max(0.0, min(1.0, value)))
        pygame.draw.rect(surface, (75, 170, 255), (x, y, fill, 12), border_radius=6)

    def draw(self, window, overlay):
        bg = (30, 33, 40)
        header = (42, 46, 56)
        border = (70, 85, 105)

        if self.is_hovered:
            border = (110, 185, 255)
            glow = pygame.Surface((self.rect.w + 16, self.rect.h + 16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (110, 185, 255, 35), glow.get_rect(), border_radius=18)
            window.blit(glow, (self.rect.x - 8, self.rect.y - 8))

        pygame.draw.rect(window, bg, self.rect, border_radius=14)
        pygame.draw.rect(window, border, self.rect, width=3, border_radius=14)

        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 55)
        pygame.draw.rect(window, header, header_rect, border_top_left_radius=14, border_top_right_radius=14)

        title = self.font_header.render(f"SAVE SLOT {self.slot_id}", True, (255, 255, 255))
        window.blit(title, (self.rect.x + 18, self.rect.y + 16))

        status = self.font_small.render("ACTIVE", True, (120, 255, 140))
        window.blit(status, (self.rect.right - status.get_width() - 18, self.rect.y + 18))

        x = self.rect.x + self.padding
        y = self.rect.y + 75

        self._label(window, "PLAYER", x, y)
        y += 22
        name = self.data.get("name", "Unknown")
        window.blit(self.font_title.render(name, True, (255, 255, 255)), (x, y))
        y += 52
        self._divider(window, y)
        y += 18

        nights = self.data.get("nights_completed", 0)
        self._label(window, "PROGRESS", x, y)
        y += 24
        self._value(window, f"Night {nights} / 7", x, y)
        y += 30
        self._progress_bar(window, x, y, self.rect.width - 44, nights / 7)
        y += 28

        money = self.data.get("money", 0)
        self._label(window, "MONEY", x, y)
        y += 22
        self._value(window, f"${money:,}", x, y)
        y += 42
        self._divider(window, y)
        y += 18

        self._label(window, "UPGRADES", x, y)
        y += 26
        upgrades = self.data.get("upgrades", [])

        if upgrades:
            for upgrade in upgrades[:4]:
                txt = self.font_small.render(f"✓ {upgrade}", True, (220, 220, 220))
                window.blit(txt, (x + 4, y))
                y += 24
            if len(upgrades) > 4:
                more = self.font_small.render(f"+{len(upgrades)-4} more...", True, (150, 150, 150))
                window.blit(more, (x + 4, y))
        else:
            txt = self.font_small.render("No upgrades unlocked", True, (120, 120, 120))
            window.blit(txt, (x + 4, y))

        created = self.data.get("date_created", "Unknown")
        date_surface = self.font_small.render(created, True, (150, 150, 150))
        window.blit(date_surface, (self.rect.x + self.padding, self.rect.bottom - 70))

        if self.is_hovered:
            self.play_button.draw(window)
            self.delete_button.draw(window)