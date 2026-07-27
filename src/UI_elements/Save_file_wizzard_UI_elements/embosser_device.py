import pygame

class EmbroiderTool:
    def __init__(self, game, pos, size, callback):
        self.game = game
        self.pos = pos
        self.callback = callback  # Function to call when a letter is pressed
        
        self.font = pygame.font.SysFont('arial', 26, bold=True)
        self.font_small = pygame.font.SysFont('arial', 16, bold=True)
        
        # Grid layout matching your concept art sketch
        # 'w' is the width multiplier for larger keys
        self.keys = [
            [{'char': 'A', 'w': 1}, {'char': 'B', 'w': 1}, {'char': 'BACK', 'w': 2}],
            [{'char': 'C', 'w': 1}, {'char': 'D', 'w': 1}, {'char': 'E', 'w': 1}],
            [{'char': 'F', 'w': 1}, {'char': 'G', 'w': 1}, {'char': 'ENTER', 'w': 2}],
            [{'char': 'H', 'w': 1}, {'char': 'I', 'w': 1}, {'char': 'J', 'w': 1}, {'char': 'K', 'w': 1}],
            [{'char': 'L', 'w': 1}, {'char': 'M', 'w': 1}, {'char': 'N', 'w': 1}, {'char': 'O', 'w': 1}],
            [{'char': 'P', 'w': 1}, {'char': 'Q', 'w': 1}, {'char': 'R', 'w': 1}, {'char': 'S', 'w': 1}],
            [{'char': 'T', 'w': 1}, {'char': 'U', 'w': 1}, {'char': 'V', 'w': 1}, {'char': 'W', 'w': 1}],
            [{'char': 'X', 'w': 1}, {'char': 'Y', 'w': 1}, {'char': 'Z', 'w': 1}]
        ]
        
        # Sizing and spacing
        self.base_size = size
        self.padding = 10
        self.bg_padding = 20
        
        # Navigation State (Gamepad/Keyboard tracking)
        self.sel_row = 0
        self.sel_col = 0
        self.last_mouse_pos = (0, 0)
        
        # Pre-calculate Rectangles for each button to make collision detection easy
        self.button_rects = []
        self._calculate_rects()

    def _calculate_rects(self):
        """Generates the absolute screen coordinates for every button."""
        self.button_rects = []
        current_y = self.pos[1] + self.bg_padding
        
        max_width = 0
        
        for row in self.keys:
            current_x = self.pos[0] + self.bg_padding
            row_rects = []
            
            for key in row:
                width = (self.base_size * key['w']) + (self.padding * (key['w'] - 1))
                rect = pygame.Rect(current_x, current_y, width, self.base_size)
                row_rects.append({'char': key['char'], 'rect': rect})
                current_x += width + self.padding
            
            self.button_rects.append(row_rects)
            
            # Track the widest row to draw the background padding correctly
            if current_x - self.pos[0] > max_width:
                max_width = current_x - self.pos[0]
                
            current_y += self.base_size + self.padding
            
        # Calculate full background size
        total_height = current_y - self.pos[1] + self.bg_padding - self.padding
        self.bg_rect = pygame.Rect(self.pos[0], self.pos[1], max_width + self.bg_padding, total_height)

    def draw(self, window):
        # 1. Draw Device Base (Dark grey plate)
        pygame.draw.rect(window, (40, 40, 45), self.bg_rect, border_radius=10)
        pygame.draw.rect(window, (20, 20, 25), self.bg_rect, width=4, border_radius=10)

        # 2. Draw Keys
        for r, row in enumerate(self.button_rects):
            for c, btn in enumerate(row):
                rect = btn['rect']
                is_selected = (r == self.sel_row and c == self.sel_col)
                
                # Colors based on selection state
                bg_color = (200, 200, 180) if is_selected else (120, 120, 110)
                text_color = (0, 0, 0) if is_selected else (40, 40, 40)
                
                # Draw the physical key
                pygame.draw.rect(window, bg_color, rect, border_radius=5)
                # 3D shadow effect on the bottom edge
                pygame.draw.rect(window, (80, 80, 75), rect, width=3, border_radius=5) 
                
                # Draw Text
                f = self.font_small if len(btn['char']) > 1 else self.font
                text_surf = f.render(btn['char'], True, text_color)
                text_rect = text_surf.get_rect(center=rect.center)
                window.blit(text_surf, text_rect)

    def update(self, delta_time):
        pass

    def handling_events(self, events):
        input_mgr = self.game.input_manager
        
        try:
            mouse_pos = pygame.mouse.get_pos()
        except:
            mouse_pos = (0,0)

        # 1. MOUSE HOVER
        if mouse_pos != self.last_mouse_pos:
            for r, row in enumerate(self.button_rects):
                for c, btn in enumerate(row):
                    if btn['rect'].collidepoint(mouse_pos):
                        self.sel_row = r
                        self.sel_col = c
            self.last_mouse_pos = mouse_pos

        # 2. MOUSE CLICK
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if we clicked the currently highlighted key
                current_btn_rect = self.button_rects[self.sel_row][self.sel_col]['rect']
                if current_btn_rect.collidepoint(mouse_pos):
                    self._press_key(self.button_rects[self.sel_row][self.sel_col]['char'])

            # 3. DIRECT KEYBOARD TYPING
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self._press_key('BACK')
                    self._highlight_key('BACK')
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._press_key('ENTER')
                    self._highlight_key('ENTER')
                elif event.unicode and event.unicode.isalpha():
                    char = event.unicode.upper()
                    self._press_key(char)
                    self._highlight_key(char) # Visually snap to the typed key

        # 4. GAMEPAD NAVIGATION
        if input_mgr.just_pressed('up'):
            self.sel_row = (self.sel_row - 1) % len(self.button_rects)
            self._clamp_col()
        elif input_mgr.just_pressed('down'):
            self.sel_row = (self.sel_row + 1) % len(self.button_rects)
            self._clamp_col()
        elif input_mgr.just_pressed('left'):
            self.sel_row, self.sel_col = self._get_prev_key(self.sel_row, self.sel_col)
        elif input_mgr.just_pressed('right'):
            self.sel_row, self.sel_col = self._get_next_key(self.sel_row, self.sel_col)
        elif input_mgr.just_pressed('action_a'):
            self._press_key(self.button_rects[self.sel_row][self.sel_col]['char'])

    def _clamp_col(self):
        """Prevents crash when moving up/down between rows of different lengths"""
        max_col = len(self.button_rects[self.sel_row]) - 1
        if self.sel_col > max_col:
            self.sel_col = max_col

    def _get_next_key(self, r, c):
        """Wraps around horizontally"""
        c += 1
        if c >= len(self.button_rects[r]):
            c = 0
            r = (r + 1) % len(self.button_rects)
        return r, c

    def _get_prev_key(self, r, c):
        """Wraps around horizontally"""
        c -= 1
        if c < 0:
            r = (r - 1) % len(self.button_rects)
            c = len(self.button_rects[r]) - 1
        return r, c

    def _highlight_key(self, target_char):
        """Snaps the gamepad selection visually to the key typed on the keyboard"""
        for r, row in enumerate(self.button_rects):
            for c, btn in enumerate(row):
                if btn['char'] == target_char:
                    self.sel_row = r
                    self.sel_col = c
                    return

    def _press_key(self, char):
        # Play a heavy mechanical clank sound here if you have one
        if hasattr(self.game, 'audio_manager'):
            pass # self.game.audio_manager.play_sound('typewriter_clank')
        
        # Send character up to the State
        self.callback(char)