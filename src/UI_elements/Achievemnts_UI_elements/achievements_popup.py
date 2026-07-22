import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from Manifests.achievements_manifest import ACHIEVEMENTS_MANIFEST
from UI_elements.Generic_UI_elements.popups import PopUp
from Tools.create_icon import create_icon

# ACHIEVEMENT POPUP FOR STATE MANAGER
class AchievementPopUp(PopUp):

    def __init__(s, game, achievement_name, duration=5):

        super().__init__(game, width=400, height=100, duration=duration, pos="bottom-right")

        s.achievement_name = achievement_name
        
        # FIX: Changed ACHIEVEMENTS to ACHIEVEMENTS_MANIFEST
        s.data = ACHIEVEMENTS_MANIFEST[achievement_name] 

        s.bg_color = (0, 0, 0, 220)
        s.icon = create_icon(size=(80, 80), colour=(0, 0, 255))

        s.font_title = pygame.font.SysFont(None, 36)
        s.font_desc = pygame.font.SysFont(None, 24)

        s.title_surface = s.font_title.render(s.achievement_name, True, (255, 255, 255))
        s.desc_surface = s.font_desc.render(s.data['mini_description'], True, (200, 200, 200))
        
        s.draw_elements()

    #DRAWING ALL THE ELEMENTS TO ONE SURFACE
    def draw_elements(s):
        s.image.blit(s.icon, (10, 10))
        s.image.blit(s.title_surface, (100, 10))
        s.image.blit(s.desc_surface, (100, 50))