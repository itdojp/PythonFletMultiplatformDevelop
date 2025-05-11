from flet import NavigationBar, NavigationDestination, icons

def create_bottom_nav(selected_index, on_nav_change):
    return NavigationBar(
        selected_index=selected_index,
        destinations=[
            NavigationDestination(icon=icons.HOME, label="ホーム"),
            NavigationDestination(icon=icons.SEARCH, label="検索"),
            NavigationDestination(icon=icons.SETTINGS, label="設定"),
        ],
        on_change=on_nav_change
    )