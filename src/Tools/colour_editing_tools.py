def hex_to_rgb(hex_color):
    """Convert a hex color string ("#RRGGBB") to an (R, G, B) tuple.

    Accepts strings starting with or without a leading '#'.
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_contrast_text_color(bg_color):
    """Return either black or white text color for readable contrast.

    Uses a simple luminance approximation to choose a contrasting color.
    Accepts a hex string or an (R, G, B) tuple.
    """
    if isinstance(bg_color, str):
        r, g, b = hex_to_rgb(bg_color)
    else:
        r, g, b = bg_color

    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 150 else (255, 255, 255)