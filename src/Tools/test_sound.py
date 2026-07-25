import pygame
import math
from array import array

def create_test_beep(frequency=440, duration=0.1):
    # Ensure mixer is initialized to grab the correct sample rate
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    sample_rate, _, channels = pygame.mixer.get_init()
    num_samples = int(sample_rate * duration)
    
    # Create a 16-bit signed integer buffer for stereo audio
    buffer = array('h', [0] * (num_samples * 2))
    
    for i in range(num_samples):
        t = i / sample_rate
        # Generate a sine wave value scaled down for comfortable volume
        value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * t))
        buffer[i * 2] = value     # Left channel
        buffer[i * 2 + 1] = value # Right channel
        
    return pygame.mixer.Sound(buffer=buffer)