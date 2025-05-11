import flet as ft
from app import create_app

def main(page: ft.Page):
    page.title = "Flet Multiplatform App"
    page.vertical_alignment = ft.MainAxisAlignment.START

    app = create_app(page)
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)