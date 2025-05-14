# theme_config.py


def get_theme():
    return {
        "color_scheme": {
            "primary": "#6200EE",
            "primary_container": "#BB86FC",
            "secondary": "#03DAC6",
            "error": "#B00020",
            "background": "#FFFFFF",
            "surface": "#FFFFFF",
            "on_primary": "#FFFFFF",
            "on_secondary": "#000000",
            "on_error": "#FFFFFF",
            "on_background": "#000000",
            "on_surface": "#000000",
        },
        "typography": {
            "font_family": "Roboto, sans-serif",
            "font_size": {
                "h1": 24,
                "h2": 20,
                "body": 16,
                "caption": 12,
            },
        },
        "spacing": {
            "small": 8,
            "medium": 16,
            "large": 24,
        },
        "border_radius": 4,
    }
