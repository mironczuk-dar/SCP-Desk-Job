#IMPORTING LIBRARIES
import pygame
from sys import exit
import threading

#IMPORTING FILES
from settings import *
from Tools.data_loading_tools import load_data, save_data

#IMPORTING STATES
from Managers.state_manager import StateManager
from Managers.audio_manager import AudioManager
from Managers.achievement_manager import AchievementManager

#IMPROTING STATES
from States.start_menu import StartMenu
from States.extras_menu import ExtrasMenu
from States.options_menu import Options

#IMPROTING FUNCTIONS FOR LOADING ASSETS
from Machines.asset_importing_machine import (
    load_menu_assets,
    load_game_assets,
    load_audio,
    )


class Game:
    
    def __str__(s):
        return 'Game made by Dariusz J. Mironczuk'
    
    def __init__(s):

        #INITALIZING PYGAME
        pygame.init()
        s.loading_in_game_data()

        #CONFIGURING DISPLAY FLAGS
        s.setting_up_display_flags()

        #INITALIZING DISPLAY
        s.display = pygame.display.set_mode((s.window_data['width'], s.window_data['height']), s.flags)
        s.window = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        s.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.mouse.set_visible(True)
        pygame.display.set_caption('[Default Pygame Project] - Game made by Dariusz J. Mironczuk')
        #pygame.display.set_icon(pygame.image.load(join(ROOT_DIR, 'assets', 'icon.png')))

        #INITALIZING CLOCK
        s.clock = pygame.time.Clock()
        s.fps = s.window_data['fps']

        #BACKGROUND THREAD TO IMPORT ASSETS WITHOUT BLOCKING STARTUP
        s.assets_loaded = False
        s.assets_thread = threading.Thread(target=s.import_assets, daemon=True)
        s.assets_thread.start()

        #SETTING UP STATES AND MANAGERS
        s.setting_up_managers()
        s.creating_states()

    def import_assets(s):
        """Load audio and other assets in background threads.

        This uses a small thread pool to parallelize expensive I/O so the UI
        can become responsive quickly while assets finish loading.
        """
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(load_audio, s),
                executor.submit(load_menu_assets, s),
                executor.submit(load_game_assets, s),
            ]
            # Wait for tasks to complete and propagate exceptions
            for f in futures:
                f.result()

        s.assets_loaded = True
        print('Assets loaded')

    def loading_in_game_data(s):
        s.window_data = load_data(WINDOW_DATA_PATH, DEFUALT_WINDOW_DATA)
        s.audio_data = load_data(AUDIO_DATA_PATH, DEFAULT_AUDIO_DATA)
        s.theme_data = load_data(THEMES_DATA_PATH, DEFAULT_THEME_DATA)
        s.controls_data = load_data(CONTROLS_DATA_PATH, DEFAULT_CONTROLS_DATA)
        s.achievements_data = load_data(ACHIEVEMENTS_DATA_PATH, DEFAULT_ACHIVEMENTS_DATA)
        s.gamefile_data = load_data(GAMEFILE_DATA_PATH, DEFAULT_GAMEFILE_DATA)

    def setting_up_display_flags(s):
        """Configure initial display flags and remember last window size."""
        s.fullscreen = s.window_data['fullscreen']
        s.last_window_size = (s.window_data['width'], s.window_data['height'])
        s.flags = pygame.FULLSCREEN if s.fullscreen else pygame.RESIZABLE

    def get_scaled_mouse_pos(s):
        """Return mouse position scaled from display space to virtual window."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale, new_w, new_h, offset_x, offset_y = s.calculate_aspect_ratio_scale_and_offset()

        # Remove the offset (black bars) from the real mouse position
        adjusted_x = mouse_x - offset_x
        adjusted_y = mouse_y - offset_y

        # Scale the coordinates back to the 1920x1080 virtual space
        virtual_x = adjusted_x / scale
        virtual_y = adjusted_y / scale

        # Clamp the values so clicking inside the black bars doesn't break UI logic
        virtual_x = max(0, min(virtual_x, WINDOW_WIDTH))
        virtual_y = max(0, min(virtual_y, WINDOW_HEIGHT))

        return int(virtual_x), int(virtual_y)
    
    def calculate_aspect_ratio_scale_and_offset(s):
        """Calculate the scale and offsets to maintain a 16:9 aspect ratio."""
        display_w, display_h = s.display.get_width(), s.display.get_height()
        target_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
        current_ratio = display_w / display_h

        if current_ratio > target_ratio:
            # Display is wider than 16:9 (Pillarbox: black bars on left/right)
            scale = display_h / WINDOW_HEIGHT
            new_w = int(WINDOW_WIDTH * scale)
            new_h = display_h
            offset_x = (display_w - new_w) // 2
            offset_y = 0
        else:
            # Display is taller than 16:9 (Letterbox: black bars on top/bottom)
            scale = display_w / WINDOW_WIDTH
            new_w = display_w
            new_h = int(WINDOW_HEIGHT * scale)
            offset_x = 0
            offset_y = (display_h - new_h) // 2

        return scale, new_w, new_h, offset_x, offset_y

    def setting_up_managers(s):
        """Create top-level managers used across the application."""
        s.state_manager = StateManager(s)
        s.audio_manager = AudioManager(s)
        s.achievements_manager = AchievementManager(s)

    def creating_states(s):
        s.state_manager.add_state('Start menu', StartMenu(s))
        s.state_manager.add_state('Extras menu', ExtrasMenu(s))
        s.state_manager.add_state('Options menu', Options(s))

        s.state_manager.set_state('Start menu')

    def save(s):
        """Persist launcher state and configuration to disk."""
        save_data(s.window_data, WINDOW_DATA_PATH)
        save_data(s.audio_data, AUDIO_DATA_PATH)
        save_data(s.controls_data, CONTROLS_DATA_PATH)
        save_data(s.theme_data, THEMES_DATA_PATH)
        save_data(s.achievements_data, ACHIEVEMENTS_DATA_PATH)

    def handling_events(s):

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                s.save()
                pygame.quit()
                exit()

            if event.type == pygame.VIDEORESIZE and not s.fullscreen:
                s.window_data['width'] = event.w
                s.window_data['height'] = event.h
                s.display = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                s.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                save_data(s.window_data, WINDOW_DATA_PATH)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    s.save()
                    pygame.quit()
                    exit()

                if event.key == pygame.K_9:
                    s.fullscreen = not s.fullscreen
                    s.window_data['fullscreen'] = s.fullscreen
                    if s.fullscreen:
                        s.last_window_size = (s.display.get_width(), s.display.get_height())
                        s.flags = pygame.FULLSCREEN
                        s.display = pygame.display.set_mode((s.window_data['width'], s.window_data['height']), s.flags)
                    else:
                        s.flags = pygame.RESIZABLE
                        s.display = pygame.display.set_mode(s.last_window_size, s.flags)
                        s.window_data['width'], s.window_data['height'] = s.last_window_size
                    save_data(s.window_data, WINDOW_DATA_PATH)

        s.state_manager.handling_events(events)

    def update(s):
        s.delta_time = s.clock.tick(s.fps) / 1000

        print(f"FPS: {s.clock.get_fps():.2f}", end='\r')
        s.state_manager.update(s.delta_time)

    def draw(s):
        """Render the active state to the virtual window and scale to the display."""
        # background fill for the virtual window
        s.window.fill((255, 0, 0))
        s.state_manager.draw(s.window)

        # 1. Get aspect-ratio correct dimensions and offsets
        scale, new_w, new_h, offset_x, offset_y = s.calculate_aspect_ratio_scale_and_offset()

        # 2. Scale the virtual window proportionally
        scaled_window = pygame.transform.scale(s.window, (new_w, new_h))

        # 3. Clear the actual display with black to create the borders
        s.display.fill((0, 0, 0))

        # 4. Blit the scaled window at the calculated center offset
        s.display.blit(scaled_window, (offset_x, offset_y))
        pygame.display.update()

    def run(s):
        """Enter the main application loop (event -> update -> draw)."""
        while True:
            s.handling_events()
            s.update()
            s.draw()


if __name__ == '__main__':
    try:
        game = Game()
        print(game)
        game.run()
    except KeyboardInterrupt:
        print("Game terminated manually.")
    except Exception:
        import traceback

        traceback.print_exc()
        input('Press [ENTER] to exit...')