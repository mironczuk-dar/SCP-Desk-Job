#CLASS FOR MANAGING ACHIEVEMENTS
class AchievementManager:

    #CONSTRUCTOR
    def __init__(s, game):

        #PASSING IN GAME AS AN ATTRIBUTE
        s.game = game

        #PLAYERS UNLOCKED ACHIEVEMENTS
        s.unlocked = s.game.achievements_data

    #METHOD FOR CHECKING IF ACHIEVEMENT SHOULD BE UNLOCKED
    def check_achievements(s):
        """Checks which achievements are unlocked based on player_data."""
        unlocked = s.unlocked

        # Example: Fish buffet
        test_achievement = sum(s.game.player_data['fish_eaten'].values())
        if total_fish >= 100 and "Fish buffet" not in unlocked:
            s.unlock_achievement("Fish buffet")

        #PLAYER SURVIVED 1 MINUTE
        if s.game.player_data['run_record_time'] >= 60000 and "Level 1 Survivor" not in unlocked:
            s.unlock_achievement("Level 1 Survivor")

        #PLAYER SURVIVED 2 MINUTES
        if s.game.player_data['run_record_time'] >= 120000 and "Level 2 Survivor" not in unlocked:
            s.unlock_achievement("Level 2 Survivor")

    #METHOD FOR UNLOCKING THE ACHIEVEMENT
    def unlock_achievement(s, name):
        """Unlock and notify StateManager."""
        s.unlocked.append(name)
        s.game.state_manager.achievement_unlocked(name)

