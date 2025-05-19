from flet import (
    NavigationRail,
    NavigationRailDestination,
    NavigationRailLabelType,
    icons,
)


class SideNav:
    def __init__(self, selected_index=0, on_select=None):
        self.selected_index = selected_index
        self.on_select = on_select

    def build(self):
        return NavigationRail(
            selected_index=self.selected_index,
            label_type=NavigationRailLabelType.ALL,
            destinations=[
                NavigationRailDestination(icon=icons.HOME, label="ホーム"),
                NavigationRailDestination(icon=icons.BOOKMARK, label="保存"),
                NavigationRailDestination(icon=icons.SETTINGS, label="設定"),
            ],
            on_change=self.on_select,
        )
