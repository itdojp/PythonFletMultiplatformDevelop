import flet as ft
from typing import Any

def get_breakpoint(page_width: float) -> str:
    if page_width < 600:
        return "mobile"
    elif page_width < 960:
        return "tablet"
    else:
        return "desktop"


def adjust_layout_for_responsive_design(page: Any) -> None:
    breakpoint = get_breakpoint(page.width)

    if breakpoint == "mobile":
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        for control in page.controls:
            control.width = page.width * 0.9
    elif breakpoint == "tablet":
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        for control in page.controls:
            control.width = page.width * 0.7
    else:
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        for control in page.controls:
            control.width = 800

    page.update()
