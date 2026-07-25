import pygame

def draw_text(window, text, pos_x, pos_y, font, colour = (0,0,0)):
    surface = font.render(text, True, colour)
    rect = surface.get_rect(center=(pos_x, pos_y))
    window.blit(surface, rect)