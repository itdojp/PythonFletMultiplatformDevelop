from flet import UserControl, Card, Column, Text, Image, Container, alignment

class AppCard(UserControl):
    def __init__(self, title, description, image_url, on_click=None):
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url
        self.on_click = on_click
    
    def build(self):
        return Card(
            elevation=4,
            content=Container(
                content=Column([
                    Image(
                        src=self.image_url,
                        width=double.infinity,
                        height=160,
                        fit=ImageFit.COVER,
                    ),
                    Container(
                        content=Column([
                            Text(self.title, weight=FontWeight.BOLD, size=16),
                            Text(self.description, size=14, color=colors.GREY_700),
                        ]),
                        padding=padding.all(16),
                    ),
                ]),
                on_click=self.on_click,
            )
        )