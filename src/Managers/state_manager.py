"""State manager for the launcher.

This module provides `StateManager`, a thin router that switches between
application states (Library, Store, Options, etc.), manages UI focus
between the sidebar and content area, and forwards events/update/draw
calls to the active state.
"""
#IMPORTING LIBRARIES
import pygame

#IMPORTING FILES
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

#IMPORTING TOOLS
from Tools.timer import Timer


class StateManager:
    """Manage application states and route input/updates/draws.

    Attributes
    - launcher: reference to the top-level `Launcher` instance
    - states: dict mapping state names to state instances
    - active_state: currently active state instance
    - ui_focus: which UI region has focus ('content' or 'sidebar')
    """

    def __init__(s, game):
        s.game = game
        s.states = {}
        s.active_state = None
        s.active_state_name = None
        s.last_state = None
        s.last_state_name = None

        #CHANGING STATE WARNING TEXT
        s.font = pygame.font.SysFont(None, 100)
        s.warning_text = s.font.render("State not found!", True, (255, 0, 0))
        s.warning_timer = Timer(2000)

    def draw_warning(s, window):
        """Draw a warning message if the state is not found."""
        if s.warning_timer.active:
            window.blit(s.warning_text, (WINDOW_WIDTH // 2 - s.warning_text.get_width() // 2, WINDOW_HEIGHT - s.warning_text.get_height() - 50))

    def add_state(s, name, state_object):
        """Register a state instance under `name`."""
        s.states[name] = state_object

    def set_state(s, name):
        """Switch to a registered state by name and trigger lifecycle hooks."""
        if name in s.states:
            if s.active_state is not None:
                s.last_state = s.active_state
                s.last_state_name = s.active_state_name

            s.active_state = s.states[name]
            s.active_state_name = name
            print(f"State changed to: {name}")

            if hasattr(s.active_state, 'on_enter'):
                s.active_state.on_enter()

            s.game.audio_manager.play_for_state(name)

        else:
            print(f"State '{name}' not found!")
            s.warning_timer.activate()

    def handling_events(s, events):
        """Handle input events and forward them to the sidebar or active state.

        The `options` key toggles focus between the sidebar and the content
        area. Events are then dispatched accordingly.
        """
        options_key = s.game.controls_data['keyboard']['options']

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == options_key:
                    pass

        if s.active_state:
                s.active_state.handling_events(events)

    def update(s, delta_time):
        """Update sidebar and the active state each frame."""
        if s.active_state:
            s.active_state.update(delta_time)

        s.warning_timer.update()

    def draw(s, window):
        """Draw the active state, then overlay the sidebar."""
        if s.active_state:
            s.active_state.draw(window)
        s.draw_warning(window)

