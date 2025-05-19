import flet as ft


def create_loading_skeleton() -> ft.Column:
    return ft.Column(
        [
            ft.Container(
                height=20,
                width=float("inf"),
                bgcolor=ft.colors.GREY_300,
                border_radius=4,
                margin=ft.margin.only(bottom=8),
            ),
            ft.Container(
                height=20,
                width=float("inf"),
                bgcolor=ft.colors.GREY_300,
                border_radius=4,
                margin=ft.margin.only(bottom=8),
            ),
            ft.Container(
                height=20,
                width=float("inf"),
                bgcolor=ft.colors.GREY_300,
                border_radius=4,
                margin=ft.margin.only(bottom=8),
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
    )
