def get_platform_specific_ui(page):
    if page.platform == "android":
        return "Android specific UI components"
    elif page.platform == "ios":
        return "iOS specific UI components"
    else:
        return "Web specific UI components"