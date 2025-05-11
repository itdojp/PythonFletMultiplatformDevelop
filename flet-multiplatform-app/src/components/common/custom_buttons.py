from flet import ElevatedButton, OutlinedButton, TextButton

def primary_button(text, on_click):
    return ElevatedButton(
        text=text,
        on_click=on_click,
        style={
            "color": "white",
            "bgcolor": "blue",
            "padding": 10,
        }
    )

def secondary_button(text, on_click):
    return OutlinedButton(
        text=text,
        on_click=on_click,
        style={
            "color": "blue",
            "padding": 10,
        }
    )

def text_button(text, on_click):
    return TextButton(
        text=text,
        on_click=on_click,
        style={
            "color": "blue",
        }
    )