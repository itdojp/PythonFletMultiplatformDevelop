from flet import Page, Column, Row, NavigationRail, Text, ElevatedButton, Theme, ColorScheme, ThemeMode
from components.navigation.bottom_nav import BottomNav
from components.navigation.side_nav import SideNav
from components.screens.home_screen import HomeScreen
from components.screens.settings_screen import SettingsScreen
from components.screens.profile_screen import ProfileScreen

class App:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Flet Multi-Platform App"
        self.page.theme = Theme(
            color_scheme=ColorScheme(
                primary=0xFF6200EE,
                secondary=0xFF03DAC6,
                background=0xFFFFFFFF,
                surface=0xFFFFFFFF,
                error=0xFFB00020,
                on_primary=0xFFFFFFFF,
                on_secondary=0xFF000000,
                on_background=0xFF000000,
                on_surface=0xFF000000,
                on_error=0xFFFFFFFF,
            )
        )
        self.page.theme_mode = ThemeMode.SYSTEM
        self.current_screen = HomeScreen()

        self.setup_ui()

    def setup_ui(self):
        self.page.add(
            Row([
                SideNav(self.navigate),
                Column([
                    self.current_screen,
                    ElevatedButton("Go to Settings", on_click=lambda e: self.navigate("settings")),
                    ElevatedButton("Go to Profile", on_click=lambda e: self.navigate("profile")),
                ])
            ])
        )

    def navigate(self, screen_name):
        if screen_name == "settings":
            self.current_screen = SettingsScreen()
        elif screen_name == "profile":
            self.current_screen = ProfileScreen()
        else:
            self.current_screen = HomeScreen()

        self.page.update()

def main(page: Page):
    app = App(page)

if __name__ == "__main__":
    main(Page())