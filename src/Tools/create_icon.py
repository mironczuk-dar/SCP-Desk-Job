import pygame

def create_icon(size=(32, 32), colour =(255, 0, 0), path=None, icon=None):
    """
    Returns a pygame.Surface to use as an icon.

    Parameters:
        size: Size of the generated default icon.
        colour: Colour of the generated default icon.
        path: Path to an image file.
        icon: Existing pygame.Surface.

    Priority:
        1. Existing Surface
        2. Image from path
        3. Generated default icon
    """

    # Use an existing Surface
    if icon is not None:
        icon = pygame.transform.scale(icon, size)
        return icon

    # Load from file
    if path is not None:
        try:
            icon = pygame.image.load(path).convert_alpha()
            icon = pygame.transform.scale(icon, size)
            return icon
        except pygame.error as e:
            print(f"Failed to load icon from '{path}': {e}")
            return None

    # Generate a default icon
    icon_surface = pygame.Surface(size, pygame.SRCALPHA)
    icon_surface.fill(colour)

    pygame.draw.rect(icon_surface, (0, 0, 0), icon_surface.get_rect(), 2)

    return icon_surface