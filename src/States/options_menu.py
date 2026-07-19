"""Options state: grouped configuration tabs for video, audio, controls, performance and themes.

This state hosts several sub-tabs that each own their own rendering and
input logic. The topbar acts as the main navigation header, while the
currently selected tab receives keyboard/controller input when
`state_manager.ui_focus == 'content'`.

Developer notes
+- Each tab is implemented in `src/UI/options_ui/` and should expose
+  `handling_events`, `update`, and `draw` methods.
+- Theme changes should call `refresh_tabs` so the tab icons and colours
+  are regenerated for the active theme.
+- `ui_focus` routing is important: topbar navigation and content editing
+  are separated by the focus state in `state_manager`.
"""
#
import pygame

from settings import THEME_LIBRARY, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_DATA_PATH, CONTROLS_DATA_PATH, get_contrast_text_color
from States.generic_state import GenericState

from UI_elements.Generic_UI_elements.buttons import GenericToggleButton
from UI_elements.Generic_UI_elements.sliders import Slider
from UI_elements.Options_UI_elements.FPS_preview_ball import Ball

from Tools.data_loading_tools import save_data


class Options(GenericState):

    def __init__(s, game):
        super().__init__(game)

        # ---------------- TABS ----------------
        s.tabs = [
            ('Video', VideoOptionsTab(game)),
            ('Audio', AudioOptionsTab(game)),
            ('Controls', ControlsOptionsTab(game)),
        ]

        s.topbar_index = 0
        s.topbar_focus_position = 1

        # ---------------- TOPBAR ----------------
        s.topbar_font = pygame.font.SysFont(None, 34)
        s.topbar_padding = (24, 12)  # horizontal, vertical padding
        s.topbar_spacing = 12
        s.topbar_y = int(WINDOW_HEIGHT * 0.06)
        s.topbar_button_height = s.topbar_font.get_height() + s.topbar_padding[1] * 2

        # Icons for tabs (generated from label initials if no assets available)
        s.topbar_icon_size = (28, 28)
        s.topbar_icon_spacing = 10
        s.topbar_icon_font = pygame.font.SysFont(None, 20)
        s.tab_icons = []
        s.generate_tab_icons()

        # Back button
        s.back_button_size = (160, 44)
        s.back_button_rect = pygame.Rect(20, 20, *s.back_button_size)
        s.back_button_hover = False

    # =====================================================

    def update(s, delta_time):
        _, active_tab = s.tabs[s.topbar_index]
        active_tab.update(delta_time)

    # =====================================================

    def draw(s, window):
        window.fill((0, 0, 0))

        # Draw a subtle separator under the top tabs
        theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        separator_y = s.topbar_y + s.topbar_button_height + 12
        pygame.draw.rect(window, theme['colour_2'], pygame.Rect(0, separator_y, WINDOW_WIDTH, 4))

        s.draw_topbar(window)

        _, active_tab = s.tabs[s.topbar_index]
        active_tab.draw(window)

    # =====================================================

    def handling_events(s, events):
        """Route keyboard/controller input to the topbar or active options tab."""
        ctrl = s.game.controls_data['keyboard']
        mouse_pos = s.game.get_scaled_mouse_pos()

        clicked_tab = None
        clicked_content = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (label, _) in enumerate(s.tabs):
                    if s.get_tab_rect(i).collidepoint(mouse_pos):
                        clicked_tab = i
                        break
                else:
                    clicked_content = True

        if clicked_tab is not None:
            s.topbar_index = clicked_tab
            s.topbar_focus_position = clicked_tab + 1
            s.game.state_manager.ui_focus = 'content'

        if clicked_content:
            s.game.state_manager.ui_focus = 'content'

        s.topbar_focus_position = max(0, min(s.topbar_focus_position, len(s.tabs)))

        for event in events:
            if event.type == pygame.MOUSEMOTION:
                s.back_button_hover = s.back_button_rect.collidepoint(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if s.back_button_rect.collidepoint(mouse_pos):
                    s.go_back()
                    return

            if event.type == pygame.KEYDOWN:
                key = event.key

                if key == pygame.K_ESCAPE:
                    s.go_back()
                    return

                # ---------- TOPBAR ----------
                if s.game.state_manager.ui_focus == 'topbar':
                    if key == ctrl['right']:
                        if s.topbar_focus_position < len(s.tabs):
                            s.topbar_focus_position += 1

                    elif key == ctrl['left']:
                        if s.topbar_focus_position > 0:
                            s.topbar_focus_position -= 1
                        else:
                            s.game.state_manager.ui_focus = 'sidebar'

                    s.topbar_focus_position = max(0, min(s.topbar_focus_position, len(s.tabs)))

                    if key == ctrl['action_a'] or key == pygame.K_RETURN:
                        if s.topbar_focus_position == 0:
                            s.go_back()
                            return
                        s.topbar_index = s.topbar_focus_position - 1
                        s.game.state_manager.ui_focus = 'content'
                        s.back_button_hover = False
                        return

                # ---------- CONTENT ----------
                elif s.game.state_manager.ui_focus == 'content':
                    if key == ctrl['action_b']:
                        s.game.state_manager.ui_focus = 'topbar'
                        s.topbar_focus_position = s.topbar_index + 1
                        return

        if s.game.state_manager.ui_focus == 'content':
            _, active_tab = s.tabs[s.topbar_index]
            active_tab.handling_events(events, ctrl)

    def draw_topbar(s, window):
        theme = THEME_LIBRARY[s.game.theme_data['current_theme']]

        # Calculate widths for each tab based on icon + label size + padding
        label_sizes = [s.topbar_font.size(label) for (label, _) in s.tabs]
        icon_w = s.topbar_icon_size[0]
        tab_widths = [icon_w + s.topbar_icon_spacing + w + s.topbar_padding[0] * 2 for (w, h) in label_sizes]
        total_width = sum(tab_widths) + s.topbar_spacing * (len(tab_widths) - 1)
        start_x = int((WINDOW_WIDTH - total_width) // 2)
        y = s.topbar_y

        focused_tab_index = s.topbar_focus_position - 1 if s.topbar_focus_position > 0 else None

        for i, (label, _) in enumerate(s.tabs):
            w = tab_widths[i]
            h = s.topbar_button_height
            x = start_x + sum(tab_widths[:i]) + s.topbar_spacing * i if i > 0 else start_x

            tab_rect = pygame.Rect(x, y, w, h)

            is_selected = (i == s.topbar_index)
            focused = (s.game.state_manager.ui_focus == 'topbar' and focused_tab_index == i)
            has_focus = (s.game.state_manager.ui_focus == 'topbar')

            if focused:
                bg_color = theme['colour_3']
                text_color = get_contrast_text_color(bg_color)
                outline_color = text_color
                outline_width = 4
            elif is_selected and has_focus:
                bg_color = theme['colour_2']
                text_color = get_contrast_text_color(bg_color)
                outline_color = text_color
                outline_width = 3
            elif is_selected:
                bg_color = theme['colour_4']
                text_color = get_contrast_text_color(bg_color)
                outline_color = theme['colour_3']
                outline_width = 2
            else:
                bg_color = theme['colour_4']
                text_color = get_contrast_text_color(bg_color)
                outline_color = (0, 0, 0)
                outline_width = 1

            # Draw rounded tab background
            pygame.draw.rect(window, bg_color, tab_rect, border_radius=12)

            # Draw outline / accent
            pygame.draw.rect(window, outline_color, tab_rect, outline_width, border_radius=12)

            # Draw icon (if generated)
            if i < len(s.tab_icons):
                icon = s.tab_icons[i]
                icon_y = tab_rect.centery - icon.get_height() // 2
                icon_x = tab_rect.x + s.topbar_padding[0]
                window.blit(icon, (icon_x, icon_y))
                text_x_offset = s.topbar_padding[0] + icon.get_width() + s.topbar_icon_spacing
            else:
                text_x_offset = s.topbar_padding[0]

            # Render text
            text_surf = s.topbar_font.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=(tab_rect.x + text_x_offset + (tab_rect.width - text_x_offset) // 2, tab_rect.centery))
            window.blit(text_surf, text_rect)

        # Draw focus underline when topbar has focus
        if s.game.state_manager.ui_focus == 'topbar':
            underline_rect = pygame.Rect(start_x, y + s.topbar_button_height + 8, total_width, 4)
            pygame.draw.rect(window, theme['colour_1'], underline_rect, border_radius=2)

        s.draw_back_button(window)

    def get_tab_rect(s, index):
        """Return the rectangle for the tab at `index` in the topbar."""
        label_sizes = [s.topbar_font.size(label) for (label, _) in s.tabs]
        icon_w = s.topbar_icon_size[0]
        tab_widths = [icon_w + s.topbar_icon_spacing + w + s.topbar_padding[0] * 2 for (w, h) in label_sizes]
        total_width = sum(tab_widths) + s.topbar_spacing * (len(tab_widths) - 1)
        start_x = int((WINDOW_WIDTH - total_width) // 2)
        y = s.topbar_y
        x = start_x + sum(tab_widths[:index]) + s.topbar_spacing * index if index > 0 else start_x
        return pygame.Rect(x, y, tab_widths[index], s.topbar_button_height)

    def draw_back_button(s, window):
        theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        focused = s.game.state_manager.ui_focus == 'topbar' and s.topbar_focus_position == 0
        bg_color = theme['colour_3'] if s.back_button_hover or focused else theme['colour_4']
        text_color = get_contrast_text_color(bg_color)

        pygame.draw.rect(window, bg_color, s.back_button_rect, border_radius=12)
        pygame.draw.rect(window, text_color, s.back_button_rect, 2, border_radius=12)

        label_surf = s.topbar_font.render('Back', True, text_color)
        window.blit(label_surf, label_surf.get_rect(center=s.back_button_rect.center))

    def go_back(s):
        prev_state = s.game.state_manager.last_state_name
        if prev_state and prev_state != 'Options menu':
            s.game.state_manager.set_state(prev_state)
        else:
            s.game.state_manager.set_state('Start menu')

    # =====================================================

    def generate_tab_icons(s):
        """Generate small circular icons for each tab using the current theme and the label initial."""
        s.tab_icons = []
        theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        for label, _ in s.tabs:
            icon_surf = pygame.Surface(s.topbar_icon_size, pygame.SRCALPHA)
            pygame.draw.circle(
                icon_surf,
                theme['colour_3'],
                (s.topbar_icon_size[0]//2, s.topbar_icon_size[1]//2),
                s.topbar_icon_size[0]//2
            )
            initial = label[0].upper()
            txt = s.topbar_icon_font.render(initial, True, theme['colour_4'])
            icon_surf.blit(txt, txt.get_rect(center=(s.topbar_icon_size[0]//2, s.topbar_icon_size[1]//2)))
            s.tab_icons.append(icon_surf)

    # =====================================================

    def on_enter(s):
        s.game.state_manager.ui_focus = 'topbar'
        s.topbar_focus_position = s.topbar_index + 1

    def refresh_tabs(s):
        """Refresh tab objects after a theme or settings update.

        This recreates the tab instances so that each tab uses the current
        theme values and any display changes are reflected immediately.
        """
        # Reinitialise ALL 5 tabs in the same order so index lengths match perfectly
        s.tabs = [
            ('Video', VideoOptionsTab(s.game)),
            ('Audio', AudioOptionsTab(s.game)),
            ('Controls', ControlsOptionsTab(s.game)),
        ]
        # Regenerate icons so they respect the newly selected theme
        s.generate_tab_icons()

class GenericOptionsTab:

    def __init__(s, game):
        s.game = game

    def update(s, delta_time):
        """Update tab-specific animations, timers, or transient UI state."""
        pass

    def draw(s, window):
        """Render the tab content into the provided surface."""
        pass

class AudioOptionsTab(GenericOptionsTab):
    """Options tab for audio volume and toggle settings.

    This tab controls music and sound settings through `AudioManager` and
    schedules preview audio playback whenever the sound volume changes.
    """

    def __init__(s, game):
        super().__init__(game)
        
        # Pull the current theme just like in VideoOptionsTab
        s.current_theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        
        s.ui_elements = []
        s.selected_index = 0  # Used for tracking keyboard navigation focus
        
        # Cooldown properties for the volume preview sound
        s.preview_cooldown_timer = 0.0
        s.preview_cooldown_duration = 0.3  # Interval in seconds between preview sounds
        s.sound_changed_flag = False        # Tracks if the volume was adjusted
        
        s.setup()

    def setup(s):
        slider_size = (800, 40)
        
        music_slider = Slider(
            s.game,
            pos=(WINDOW_WIDTH/2 - slider_size[0]/2, WINDOW_HEIGHT/3),
            size=slider_size,
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("music_volume", 1.0),
            on_change=lambda v: s.game.audio_manager.set_music_volume(v)
        )

        # Redirected on_change to our custom tracker method
        sound_slider = Slider(
            s.game,
            pos=(WINDOW_WIDTH/2 - slider_size[0]/2, WINDOW_HEIGHT/3*2),
            size=slider_size,
            min_val=0,
            max_val=1,
            start_val=s.game.audio_data.get("sound_volume", 1.0),
            on_change=s.handle_sound_volume_change
        )

        music_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3 + slider_size[1] + 50),
            text="Music",
            action=s.game.audio_manager.toggle_music
        )

        sound_toggle = GenericToggleButton(
            s.game,
            size=(220, 50),
            pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT/3*2 + slider_size[1] + 50),
            text="Sound",
            action=s.game.audio_manager.toggle_sound
        )

        s.ui_elements.extend([
            music_slider,
            music_toggle,
            sound_slider,
            sound_toggle
        ])

    def handle_sound_volume_change(s, v):
        """Update the sound volume and mark the change for a preview sound."""
        s.game.audio_manager.set_sound_volume(v)
        s.sound_changed_flag = True

    def handling_events(s, events, ctrl):
        """Handle keyboard and UI element events inside the audio tab."""
        if s.game.state_manager.ui_focus != 'content':
            return

        # 1. Capture the single KEYDOWN event from the queue
        current_key = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                current_key = event.key
                break 

        if current_key is None:
            # Still process mouse events for elements if needed
            for element in s.ui_elements:
                if hasattr(element, 'handling_events'):
                    try:
                        element.handling_events(events, ctrl)
                    except TypeError:
                        element.handling_events(events)
            return

        # 2. Map current_key to logical navigation actions
        is_up = current_key == ctrl['up']
        is_down = current_key == ctrl['down']
        is_left = current_key == ctrl['left']
        is_right = current_key == ctrl['right']
        is_confirm = current_key in [ctrl['action_a'], pygame.K_RETURN]

        # --- VERTICAL NAVIGATION ---
        if is_up:
            s.selected_index = (s.selected_index - 1) % len(s.ui_elements)
        elif is_down:
            s.selected_index = (s.selected_index + 1) % len(s.ui_elements)

        # Update the s.is_selected flags so elements know who has focus
        for i, element in enumerate(s.ui_elements):
            if hasattr(element, 'is_selected'):
                element.is_selected = (i == s.selected_index)

        # 3. --- DISPATCH INTERACTION TO ACTIVE ELEMENT ---
        active_element = s.ui_elements[s.selected_index]

        # Case A: Active element is a Slider
        if active_element.__class__.__name__ == "Slider":
            if is_left:
                active_element.change_value(-active_element.step)
            elif is_right:
                active_element.change_value(active_element.step)

        # Case B: Active element is a Button / Toggle Button
        elif is_confirm:
            if hasattr(active_element, 'activate'):
                active_element.activate()
            elif hasattr(active_element, 'action') and active_element.action:
                active_element.action()

        # Pass remaining raw events (like mouse events) safely down to the element
        if hasattr(active_element, 'handling_events'):
            try:
                active_element.handling_events(events, ctrl)
            except TypeError:
                active_element.handling_events(events)

    def update(s, delta_time):
        """Update internal timers and UI elements each frame."""
        # Update logic for sliders/buttons
        for element in s.ui_elements:
            if hasattr(element, 'update'):
                element.update(delta_time)

        # --- PREVIEW COOLDOWN TIMER ---
        if s.preview_cooldown_timer > 0:
            s.preview_cooldown_timer -= delta_time

        # If a sound volume change occurred and our cooldown is ready, play sound
        if s.sound_changed_flag and s.preview_cooldown_timer <= 0:
            # Calls your audio manager to trigger a quick test blip/noise
            if hasattr(s.game.audio_manager, 'play_sound_preview'):
                s.game.audio_manager.play_sound_preview()
            elif hasattr(s.game.audio_manager, 'play_preview_sound'):
                s.game.audio_manager.play_preview_sound()

            s.sound_changed_flag = False
            s.preview_cooldown_timer = s.preview_cooldown_duration

    def draw(s, window):
        """Draw the audio controls and highlight the focused element."""
        has_focus = (s.game.state_manager.ui_focus == 'content')
        
        for i, element in enumerate(s.ui_elements):
            is_selected = (i == s.selected_index)
            
            if hasattr(element, 'draw'):
                try:
                    element.draw(window, is_focused=(is_selected and has_focus))
                except TypeError:
                    element.draw(window)

class ControlsOptionsTab(GenericOptionsTab):
    """Options tab for control presets and key rebinding."""
    def __init__(s, game):
        super().__init__(game)

        s.current_theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        
        # --- Layout for the preset selector and rebinding panels ---
        s.initial_pos = (WINDOW_WIDTH * 0.25, 430) 
        s.button_size = (460, 130)  # Expanded size to gracefully house both text and images
        s.spacing = 15
        s.column_spacing = 700
        
        s.font = pygame.font.SysFont(None, 60, False)
        s.preset_font = pygame.font.SysFont(None, 40, True)
        s.title_font = pygame.font.SysFont(None, 70, False)
        s.value_font = pygame.font.SysFont(None, 45, False)

        # Map pygame.key.name strings to your exact launcher.button_images keys
        s.asset_mapping = {
            'up': 'up_arrow_button',
            'down': 'down_arrow_button',
            'left': 'left_arrow_button',
            'right': 'right_arrow_button',
            'return': 'enter_button',
            'tab': 'tab_button',
            'action_a': 'r_button',
            'action_b': 'e_button',
        }

        # --- PRESET CONFIGURATION ---
        s.preset_names = ['Arrows', 'WASD', 'Custom']
        s.presets = {
            'Arrows': {
                'up': pygame.K_UP, 'down': pygame.K_DOWN, 
                'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
                'action_a': pygame.K_r, 'action_b': pygame.K_e
            },
            'WASD': {
                'up': pygame.K_w, 'down': pygame.K_s, 
                'left': pygame.K_a, 'right': pygame.K_d,
                'action_a': pygame.K_p, 'action_b': pygame.K_o
            }
        }
        
        s.focus_area = 'preset'  # Starts on 'preset', can switch to 'bindings'
        s.preset_idx = 2         # The currently active preset (Defaults to Custom)
        s.preset_focus_idx = 2   # Which preset button the cursor is hovering over
        
        # Check current keys on boot
        s.evaluate_current_preset()

        # Group components back into clearly labeled rows across two columns
        s.columns = {
            'left': ['up', 'down', 'left', 'right'],
            'right': ['options', 'action_a', 'action_b']
        }
        s.column_names = ['left', 'right']
        s.column_titles = ['Movement Buttons', 'Action Buttons']
        
        s.active_col_idx = 0  # 0: left, 1: right
        s.selected_index = 0  # Row index within the current column
        
        s.waiting_for_key = False

    def evaluate_current_preset(s):
        """Detect whether the current bindings match a known preset."""
        ctrl = s.game.controls_data['keyboard']
        s.preset_idx = 2  # Default to Custom
        for idx, name in enumerate(['Arrows', 'WASD']):
            preset = s.presets[name]
            if all(ctrl.get(k) == preset[k] for k in preset):
                s.preset_idx = idx
                break
        
        s.preset_focus_idx = s.preset_idx

    def apply_preset(s):
        """Apply the selected control preset and persist it to disk."""
        preset_name = s.preset_names[s.preset_idx]
        if preset_name == 'Custom':
            return
        
        preset_data = s.presets[preset_name]
        for key, val in preset_data.items():
            s.game.controls_data['keyboard'][key] = val
            
        save_data(s.game.controls_data, CONTROLS_DATA_PATH)

    def handling_events(s, events, ctrl):
        if s.game.state_manager.ui_focus != 'content':
            return

        mouse_pos = s.game.get_scaled_mouse_pos()
        current_key = None
        mouse_click = False

        for event in events:
            if event.type == pygame.KEYDOWN and current_key is None:
                current_key = event.key

            if event.type == pygame.MOUSEMOTION:
                for i in range(len(s.preset_names)):
                    if s.get_preset_button_rect(i).collidepoint(mouse_pos):
                        s.focus_area = 'preset'
                        s.preset_focus_idx = i
                        break
                else:
                    for col_idx, col_name in enumerate(s.column_names):
                        for row_idx, _ in enumerate(s.columns[col_name]):
                            if s.get_binding_rect(col_idx, row_idx).collidepoint(mouse_pos):
                                s.focus_area = 'bindings'
                                s.active_col_idx = col_idx
                                s.selected_index = row_idx
                                break
                        else:
                            continue
                        break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
                for i in range(len(s.preset_names)):
                    if s.get_preset_button_rect(i).collidepoint(mouse_pos):
                        s.focus_area = 'preset'
                        s.preset_focus_idx = i
                        s.preset_idx = i
                        s.apply_preset()
                        break
                else:
                    for col_idx, col_name in enumerate(s.column_names):
                        for row_idx, _ in enumerate(s.columns[col_name]):
                            if s.get_binding_rect(col_idx, row_idx).collidepoint(mouse_pos):
                                s.focus_area = 'bindings'
                                s.active_col_idx = col_idx
                                s.selected_index = row_idx
                                s.waiting_for_key = True
                                break
                        else:
                            continue
                        break

        if current_key is not None and s.waiting_for_key:
            if current_key != pygame.K_ESCAPE:
                col_key = s.column_names[s.active_col_idx]
                action_name = s.columns[col_key][s.selected_index]
                s.update_control(action_name, current_key)
                s.preset_idx = 2
                s.preset_focus_idx = 2
            s.waiting_for_key = False
            return

        if s.waiting_for_key or current_key is None:
            return

        is_up = current_key == ctrl['up']
        is_down = current_key == ctrl['down']
        is_left = current_key == ctrl['left']
        is_right = current_key == ctrl['right']
        is_confirm = current_key in [ctrl['action_a'], pygame.K_RETURN]

        # --- PRESET SELECTOR NAVIGATION ---
        if s.focus_area == 'preset':
            if is_left:
                s.preset_focus_idx = max(0, s.preset_focus_idx - 1)
            elif is_right:
                s.preset_focus_idx = min(len(s.preset_names) - 1, s.preset_focus_idx + 1)
            elif is_confirm:
                s.preset_idx = s.preset_focus_idx
                s.apply_preset()
            elif is_down:
                s.focus_area = 'bindings'  
            return  

        # --- BINDINGS COLUMN NAVIGATION ---
        current_col_key = s.column_names[s.active_col_idx]
        num_items = len(s.columns[current_col_key])

        if is_left:
            s.active_col_idx = max(0, s.active_col_idx - 1)
            s.selected_index = min(s.selected_index, len(s.columns[s.column_names[s.active_col_idx]]) - 1)
        elif is_right:
            s.active_col_idx = min(len(s.column_names) - 1, s.active_col_idx + 1)
            s.selected_index = min(s.selected_index, len(s.columns[s.column_names[s.active_col_idx]]) - 1)

        if is_up:
            if s.selected_index == 0:
                s.focus_area = 'preset'
                s.preset_focus_idx = s.preset_idx  # Snap cursor back to active preset
            else:
                s.selected_index -= 1
        elif is_down:
            s.selected_index = min(num_items - 1, s.selected_index + 1)

        if is_confirm:
            s.waiting_for_key = True

    def draw(s, window):
        has_focus = (s.game.state_manager.ui_focus == 'content')
        pressed_keys = pygame.key.get_pressed()
        
        # ---------------------------------------------------------
        # 1. DRAW PRESET SELECTOR
        # ---------------------------------------------------------
        preset_y = s.initial_pos[1] - 230
        p_btn_w, p_btn_h, p_spacing = 200, 60, 30
        total_preset_width = (p_btn_w * 3) + (p_spacing * 2)
        start_x = (WINDOW_WIDTH - total_preset_width) // 2 + 100

        p_title_surf = s.value_font.render("Control Scheme", True, s.current_theme['colour_2'])
        window.blit(p_title_surf, p_title_surf.get_rect(midbottom=(WINDOW_WIDTH // 2 +100, preset_y - 20)))

        for i, preset_name in enumerate(s.preset_names):
            x = start_x + i * (p_btn_w + p_spacing)
            rect = pygame.Rect(x, preset_y, p_btn_w, p_btn_h)
            
            is_active = (i == s.preset_idx)
            is_focused = (i == s.preset_focus_idx and s.focus_area == 'preset' and has_focus)

            bg_colour = s.current_theme['colour_2'] if is_active else s.current_theme['colour_4']
            text_colour = get_contrast_text_color(bg_colour)

            pygame.draw.rect(window, bg_colour, rect, border_radius=12)
            if is_focused:
                pygame.draw.rect(window, (255, 200, 0), rect, 4, border_radius=15)

            text_surf = s.preset_font.render(preset_name, True, text_colour)
            window.blit(text_surf, text_surf.get_rect(center=rect.center))

        # ---------------------------------------------------------
        # 2. DRAW TWO-COLUMN BINDINGS BOXES
        # ---------------------------------------------------------
        for col_idx, col_name in enumerate(s.column_names):
            title = s.column_titles[col_idx]
            x = s.initial_pos[0] + col_idx * s.column_spacing + s.button_size[0] // 2
            y = s.initial_pos[1] - 40
            
            title_surf = s.title_font.render(title, True, s.current_theme['colour_2'])
            window.blit(title_surf, title_surf.get_rect(center=(x, y)))
        
        for col_idx, col_name in enumerate(s.column_names):
            actions = s.columns[col_name]
            
            for row_idx, action_name in enumerate(actions):
                is_selected = (col_idx == s.active_col_idx and row_idx == s.selected_index and s.focus_area == 'bindings')
                is_waiting = (is_selected and s.waiting_for_key)
                
                if is_waiting:
                    bg_colour = (200, 50, 50)
                elif is_selected and has_focus:
                    bg_colour = s.current_theme['colour_2']
                else:
                    bg_colour = s.current_theme['colour_4']

                text_colour = get_contrast_text_color(bg_colour)

                x = s.initial_pos[0] + col_idx * s.column_spacing
                y = s.initial_pos[1] + row_idx * (s.button_size[1] + s.spacing)

                rect = pygame.Rect(x, y, s.button_size[0], s.button_size[1])
                pygame.draw.rect(window, bg_colour, rect, border_radius=12)
                
                # Draw yellow border indicator to clearly show where user is browsing
                if is_selected and has_focus:
                    pygame.draw.rect(window, (255, 200, 0), rect, 4, border_radius=15)

                if is_waiting:
                    prompt_surf = s.value_font.render("PRESS...", True, text_colour)
                    window.blit(prompt_surf, prompt_surf.get_rect(center=rect.center))
                else:
                    # A. Render the action label text on the left side of the panel
                    label_txt = action_name.replace('_', ' ').title()
                    label_surf = s.value_font.render(f"{label_txt}:", True, text_colour)
                    window.blit(label_surf, label_surf.get_rect(midleft=(rect.left + 25, rect.centery)))

                    # B. Pull keyboard codes & calculate active pressed statuses
                    key_code = s.game.controls_data['keyboard'][action_name]
                    pygame_name = pygame.key.name(key_code).lower()
                    
                    base_image_key = s.asset_mapping.get(pygame_name, f"{pygame_name}_button")
                    image_key = f"{base_image_key}_pressed" if pressed_keys[key_code] else base_image_key

                    btn_img = None
                    if image_key in s.game.button_images:
                        btn_img = s.game.button_images[image_key]
                    elif base_image_key in s.game.button_images:
                        btn_img = s.game.button_images[base_image_key]

                    # C. Draw button graphics on the right side of the box panel
                    if btn_img:
                        img_rect = btn_img.get_rect(midright=(rect.right - 25, rect.centery))
                        window.blit(btn_img, img_rect.topleft)
                    else:
                        # Clean fallback to capital text string strings if images are missing
                        fallback_text = s.value_font.render(pygame_name.upper(), True, text_colour)
                        window.blit(fallback_text, fallback_text.get_rect(midright=(rect.right - 25, rect.centery)))

    def update_control(s, action_name, new_key):
        s.game.controls_data['keyboard'][action_name] = new_key
        save_data(s.game.controls_data, CONTROLS_DATA_PATH)

    def get_preset_button_rect(s, index):
        preset_y = s.initial_pos[1] - 230
        p_btn_w, p_btn_h, p_spacing = 200, 60, 30
        total_preset_width = (p_btn_w * 3) + (p_spacing * 2)
        start_x = (WINDOW_WIDTH - total_preset_width) // 2 + 100
        x = start_x + index * (p_btn_w + p_spacing)
        return pygame.Rect(x, preset_y, p_btn_w, p_btn_h)

    def get_binding_rect(s, col_idx, row_idx):
        x = s.initial_pos[0] + col_idx * s.column_spacing
        y = s.initial_pos[1] + row_idx * (s.button_size[1] + s.spacing)
        return pygame.Rect(x, y, s.button_size[0], s.button_size[1])

class VideoOptionsTab(GenericOptionsTab):
    """Options tab that exposes resolution and framerate controls.

    This tab supports keyboard navigation across a resolution grid and
    an FPS list, and it writes the selected values back to launcher
    settings so the change is immediately visible.
    """

    def __init__(s, game):
        super().__init__(game)

        s.current_theme = THEME_LIBRARY[s.game.theme_data['current_theme']]
        
        # Responsive layout based on aspect ratio
        s.aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
        
        # Resolution options as ordered list for grid layout
        # Optimized for Raspberry Pi and various displays
        s.resolution_list = [
            ('Fullscreen', None),
            ('1920x1080 (16:9)', [1920, 1080]),
            ('1280x720 (16:9)', [1280, 720]),
            ('1024x600 (17:10)', [1024, 600]),
            ('800x600 (4:3)', [800, 600]),
            ('800x480 (16:9)', [800, 480]),
            ('640x480 (4:3)', [640, 480]),
            ('640x360 (16:9)', [640, 360]),
            ('720x480 (3:2)', [720, 480])
        ]
        
        # Grid layout: 2 columns on the left for resolutions
        s.resolution_cols = 2
        s.resolution_button_width = int(WINDOW_WIDTH * 0.18)
        s.resolution_button_height = int(WINDOW_HEIGHT * 0.11)
        s.resolution_spacing_x = int(WINDOW_WIDTH * 0.015)
        s.resolution_spacing_y = int(WINDOW_HEIGHT * 0.015)
        s.resolution_grid_start_x = int(WINDOW_WIDTH * 0.12)
        s.resolution_grid_start_y = int(WINDOW_HEIGHT * 0.20)
        
        # FPS column in the middle, 1 column layout
        s.fps_col_x = int(WINDOW_WIDTH * 0.55)
        s.fps_button_width = int(WINDOW_WIDTH * 0.18)
        s.fps_button_height = int(WINDOW_HEIGHT * 0.08)
        s.fps_spacing_y = int(WINDOW_HEIGHT * 0.015)
        s.fps_col_start_y = int(WINDOW_HEIGHT * 0.20)
        
        # FPS preview ball positioned to the right of FPS buttons
        s.ball_x = int(WINDOW_WIDTH * 0.88)
        s.ball_y = int(WINDOW_HEIGHT * 0.35)
        
        # Responsive fonts
        s.font = pygame.font.SysFont(None, int(WINDOW_HEIGHT * 0.06), False)
        s.value_font = pygame.font.SysFont(None, int(WINDOW_HEIGHT * 0.035), False)
        s.header_font = pygame.font.SysFont(None, int(WINDOW_HEIGHT * 0.04), True)
        s.fps_label_font = pygame.font.SysFont(None, int(WINDOW_HEIGHT * 0.03), False)
        
        s.FPS_options = ['Uncapped', 90, 60, 30, 15]

        s.FPS_preview_ball = Ball((s.ball_x, s.ball_y), s.current_theme['colour_2'])

        s.active_column = 'resolution'   # 'resolution' | 'fps'
        s.resolution_index = 0
        s.fps_index = 0

        s.selected_resolution = None
        s.selected_fps = None

    def handling_events(s, events, ctrl):
        if s.game.state_manager.ui_focus != 'content':
            return

        mouse_pos = s.game.get_scaled_mouse_pos()
        clicked = False
        current_key = None

        for event in events:
            if event.type == pygame.KEYDOWN and current_key is None:
                current_key = event.key

            if event.type == pygame.MOUSEMOTION:
                for i in range(len(s.resolution_list)):
                    if s.get_resolution_grid_rect(i).collidepoint(mouse_pos):
                        s.active_column = 'resolution'
                        s.resolution_index = i
                        break
                else:
                    for i in range(len(s.FPS_options)):
                        if s.get_fps_rect(i).collidepoint(mouse_pos):
                            s.active_column = 'fps'
                            s.fps_index = i
                            break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(len(s.resolution_list)):
                    if s.get_resolution_grid_rect(i).collidepoint(mouse_pos):
                        s.active_column = 'resolution'
                        s.resolution_index = i
                        s.apply_resolution_selection()
                        clicked = True
                        break
                if clicked:
                    continue
                for i in range(len(s.FPS_options)):
                    if s.get_fps_rect(i).collidepoint(mouse_pos):
                        s.active_column = 'fps'
                        s.fps_index = i
                        s.apply_fps_selection()
                        clicked = True
                        break

        if current_key is None and clicked:
            return

        if current_key is None:
            return

        is_up = current_key == ctrl['up']
        is_down = current_key == ctrl['down']
        is_left = current_key == ctrl['left']
        is_right = current_key == ctrl['right']
        is_confirm = current_key in [ctrl['action_a'], pygame.K_RETURN]

        # --- MOVE UP / DOWN / LEFT / RIGHT ---
        if s.active_column == 'resolution':
            col = s.resolution_index % s.resolution_cols
            row = s.resolution_index // s.resolution_cols

            if is_up and row > 0:
                s.resolution_index -= s.resolution_cols
            elif is_down and (row + 1) * s.resolution_cols + col < len(s.resolution_list):
                s.resolution_index += s.resolution_cols

            if is_left and col > 0:
                s.resolution_index -= 1
            elif is_right:
                if col < s.resolution_cols - 1:
                    s.resolution_index += 1
                else:
                    s.active_column = 'fps'

        else:  # fps column
            if is_up and s.fps_index > 0:
                s.fps_index -= 1
            elif is_down and s.fps_index < len(s.FPS_options) - 1:
                s.fps_index += 1

            if is_left:
                s.active_column = 'resolution'
                row = min(s.fps_index, (len(s.resolution_list) - 1) // s.resolution_cols)
                s.resolution_index = row * s.resolution_cols + (s.resolution_cols - 1)

        if is_confirm:
            if s.active_column == 'resolution':
                s.apply_resolution_selection()
            else:
                s.apply_fps_selection()

    def update(s, delta_time):
        s.FPS_preview_ball.update(delta_time)

    def draw(s, window):
        has_focus = (s.game.state_manager.ui_focus == 'content')

        s.FPS_preview_ball.draw(window)
        
        # Draw headers
        res_header = s.header_font.render("Resolution", True, s.current_theme['colour_2'])
        window.blit(res_header, (s.resolution_grid_start_x, s.resolution_grid_start_y - int(WINDOW_HEIGHT * 0.06)))
        
        fps_header = s.header_font.render("FPS", True, s.current_theme['colour_2'])
        window.blit(fps_header, (s.fps_col_x, s.fps_col_start_y - int(WINDOW_HEIGHT * 0.06)))

        s.draw_resolution_grid(window, has_focus)
        s.draw_FPS_buttons(window, has_focus)
        s.draw_current_settings(window)

    def get_resolution_grid_pos(s, index):
        """Calculate grid position for a resolution button."""
        row = index // s.resolution_cols
        col = index % s.resolution_cols
        x = s.resolution_grid_start_x + col * (s.resolution_button_width + s.resolution_spacing_x)
        y = s.resolution_grid_start_y + row * (s.resolution_button_height + s.resolution_spacing_y)
        return x, y

    def draw_resolution_grid(s, window, has_focus):
        for i, (res_label, res_dims) in enumerate(s.resolution_list):
            is_selected = (s.active_column == 'resolution' and i == s.resolution_index)
            is_current = s.is_current_resolution(res_label)

            bg_colour = (
                s.current_theme['colour_2']
                if is_selected and has_focus
                else s.current_theme['colour_4']
            )

            text_colour = get_contrast_text_color(bg_colour)
            x, y = s.get_resolution_grid_pos(i)

            rect = pygame.Rect(x, y, s.resolution_button_width, s.resolution_button_height)
            pygame.draw.rect(window, bg_colour, rect, border_radius=8)

            # Current resolution indicator
            if is_current:
                pygame.draw.rect(window, (0, 200, 0), rect, 4, border_radius=8)

            # Focus indicator
            if is_selected and has_focus:
                pygame.draw.rect(window, (255, 200, 0), rect, 3, border_radius=8)

            # Text - fit resolution label into button
            display_text = res_label
            text_surf = s.value_font.render(display_text, True, text_colour)
            
            # Scale down text if it's too wide
            max_text_width = s.resolution_button_width - int(WINDOW_WIDTH * 0.01)
            if text_surf.get_width() > max_text_width:
                scale_factor = max_text_width / text_surf.get_width()
                scaled_font_size = max(int(s.value_font.get_height() * scale_factor), 10)
                small_font = pygame.font.SysFont(None, scaled_font_size, False)
                text_surf = small_font.render(display_text, True, text_colour)
            
            text_rect = text_surf.get_rect(center=rect.center)
            window.blit(text_surf, text_rect)

    def draw_FPS_buttons(s, window, has_focus):
        for i, fps in enumerate(s.FPS_options):

            is_selected = (
                s.active_column == 'fps' and
                i == s.fps_index
            )

            is_current = s.is_current_fps(fps)

            bg_colour = (
                s.current_theme['colour_2']
                if is_selected and has_focus
                else s.current_theme['colour_4']
            )

            text_colour = get_contrast_text_color(bg_colour)

            x = s.fps_col_x
            y = s.fps_col_start_y + i * (s.fps_button_height + s.fps_spacing_y)
            
            rect = pygame.Rect(x, y, s.fps_button_width, s.fps_button_height)
            pygame.draw.rect(window, bg_colour, rect, border_radius=8)

            # Current FPS indicator
            if is_current:
                pygame.draw.rect(window, (0, 200, 0), rect, 4, border_radius=8)

            # Focus indicator
            if is_selected and has_focus:
                pygame.draw.rect(window, (255, 200, 0), rect, 3, border_radius=8)

            fps_text = str(fps) if fps != 'Uncapped' else 'Uncapped'
            text_surface = s.fps_label_font.render(fps_text, True, text_colour)
            text_rect = text_surface.get_rect(center=rect.center)
            window.blit(text_surface, text_rect)

    def get_fps_values(s):
        """Return the full list of available FPS options."""
        return s.FPS_options

    def get_resolution_grid_rect(s, index):
        x, y = s.get_resolution_grid_pos(index)
        return pygame.Rect(x, y, s.resolution_button_width, s.resolution_button_height)

    def get_fps_rect(s, index):
        x = s.fps_col_x
        y = s.fps_col_start_y + index * (s.fps_button_height + s.fps_spacing_y)
        return pygame.Rect(x, y, s.fps_button_width, s.fps_button_height)

    def apply_resolution_selection(s):
        res_label, res_dims = s.resolution_list[s.resolution_index]
        if res_label == 'Fullscreen':
            s.go_fullscreen()
        else:
            width, height = res_dims
            s.change_resolution(width, height)

    def apply_fps_selection(s):
        fps = s.FPS_options[s.fps_index]
        if fps == 'Uncapped':
            s.update_fps(1000)
        else:
            s.update_fps(fps)

    def is_current_fps(s, fps):
        """Return whether the given FPS option matches the current launcher FPS."""
        if fps == 'Uncapped':
            return s.game.window_data['fps'] == 0
        return s.game.window_data['fps'] == fps

    def is_current_resolution(s, res_label):
        """Return whether `res_label` represents the current active resolution."""
        if res_label == 'Fullscreen':
            return s.game.window_data['fullscreen']

        # Find dimensions for this label
        for label, dims in s.resolution_list:
            if label == res_label and dims is not None:
                width, height = dims
                return (
                    not s.game.window_data['fullscreen'] and
                    s.game.window_data['width'] == width and
                    s.game.window_data['height'] == height
                )
        return False

    def change_resolution(s, width, height):
        """Apply a new window resolution and persist the selected size."""

        s.game.window_data['width'] = width
        s.game.window_data['height'] = height
        s.game.display = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        #SAVING CHANGES
        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def go_fullscreen(s):
        """Toggle fullscreen mode and persist the new window state."""

        s.game.fullscreen = not s.game.fullscreen
        s.game.window_data['fullscreen'] = s.game.fullscreen

        if s.game.fullscreen:
            s.game.last_window_size = (s.game.display.get_width(), s.game.display.get_height())
            s.game.flags = pygame.FULLSCREEN
            s.game.display = pygame.display.set_mode((s.game.window_data['width'], s.game.window_data['height']), s.game.flags)
        else:
            s.game.flags = pygame.RESIZABLE
            s.game.display = pygame.display.set_mode(s.game.last_window_size, s.game.flags)
            s.game.window_data['width'], s.game.window_data['height'] = s.game.last_window_size

        #SAVING CHANGES
        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def update_fps(s, new_fps):
        """Set the launcher FPS cap and persist the selection."""
        s.game.fps = None if new_fps == 0 else new_fps
        s.game.window_data['fps'] = new_fps

        save_data(s.game.window_data, WINDOW_DATA_PATH)

    def draw_current_settings(s, window):
        """Render a status line with the currently applied resolution/FPS."""
        text = f"Resolution: {s.game.window_data['width']}x{s.game.window_data['height']} | FPS: "
        text += "Uncapped" if s.game.window_data['fps'] == 0 else str(s.game.window_data['fps'])

        surf = s.font.render(text, True, s.current_theme['colour_2'])
        window.blit(surf, (s.resolution_grid_start_x, WINDOW_HEIGHT - int(WINDOW_HEIGHT * 0.12)))