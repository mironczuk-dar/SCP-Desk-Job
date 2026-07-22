import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from UI_elements.Achievemnts_UI_elements.achievements_popup import AchievementPopUp

class AchievementManager:

    # CONSTRUCTOR
    def __init__(s, game):
        # PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        # PLAYERS UNLOCKED ACHIEVEMENTS
        s.unlocked = s.game.achievements_data
        
        # POPUP MANAGEMENT
        s.popup_group = pygame.sprite.Group()
        s.active_popups = [] # List used to track order for stacking

    # METHOD FOR UPDATING THE ACHIEVEMENT MANAGER
    def update(s):
        """Update the achievement manager and handle popup stacking."""
        s.check_achievements()
        
        # Grab delta_time directly from the game object
        delta_time = s.game.delta_time
        
        # Clean up dead popups and manage dynamic stacking positions
        alive_popups = []
        for i, popup in enumerate(s.active_popups):
            if popup.alive():
                # Calculate target bottom: Base margin + (index * (height + padding))
                target_bottom = WINDOW_HEIGHT - 20 - (i * (popup.height + 10))
                
                # If a popup below this one vanished, smoothly slide it down
                if popup.rect.bottom < target_bottom:
                    popup.rect.bottom += int(400 * delta_time)
                    if popup.rect.bottom > target_bottom:
                        popup.rect.bottom = target_bottom
                # If it's a new popup, snap it to the correct stack position immediately
                elif popup.rect.bottom > target_bottom:
                    popup.rect.bottom = target_bottom
                    
                alive_popups.append(popup)
                
        s.active_popups = alive_popups
        
        # Update the popups (handles the horizontal sliding and timers)
        s.popup_group.update(delta_time)

    # METHOD FOR DRAWING THE ACHIEVEMENTS
    def draw(s, window):
        """Draw the achievement manager popups."""
        s.popup_group.draw(window)

    # METHOD FOR CHECKING IF ACHIEVEMENT SHOULD BE UNLOCKED
    def check_achievements(s):
        """Checks which achievements are unlocked based on player_data."""
        unlocked = s.unlocked

        #PLAYER LAUNCHED THE GAME
        if 'Test achievement' not in unlocked:
            s.unlock_achievement('Test achievement')

        '''
        # Example code:
        test_achievement = sum(s.game.player_data['fish_eaten'].values())
        if total_fish >= 100 and "Fish buffet" not in unlocked:
            s.unlock_achievement("Fish buffet")

        #PLAYER SURVIVED 1 MINUTE
        if s.game.player_data['run_record_time'] >= 60000 and "Level 1 Survivor" not in unlocked:
            s.unlock_achievement("Level 1 Survivor")

        #PLAYER SURVIVED 2 MINUTES
        if s.game.player_data['run_record_time'] >= 120000 and "Level 2 Survivor" not in unlocked:
            s.unlock_achievement("Level 2 Survivor")
        '''

    # METHOD FOR UNLOCKING THE ACHIEVEMENT
    def unlock_achievement(s, name):
        """Unlock, instantiate the popup, and append to manager."""
        s.unlocked.append(name)
        
        # Create the popup
        new_popup = AchievementPopUp(s.game, name)
        
        # Immediately adjust its Y-position so it stacks above existing popups
        stack_index = len(s.active_popups)
        target_bottom = WINDOW_HEIGHT - 20 - (stack_index * (new_popup.height + 10))
        new_popup.rect.bottom = target_bottom
        
        # Add to both the list (for stack tracking) and the sprite group (for drawing/updating)
        s.active_popups.append(new_popup)
        s.popup_group.add(new_popup)