"""アプリケーションで使用するカード形式のUIコンポーネントを提供するモジュール。

このモジュールは、画像、タイトル、説明文を含むカード形式のUIコンポーネントを提供します。
レスポンシブデザインに対応しており、様々な画面サイズに適応します。
"""

from flet import Card, Column, Container, Image, Text, UserControl, alignment, colors, padding
from flet import ImageFit, FontWeight
from typing import Optional, Callable, Any
import math


class AppCard(UserControl):
    """アプリケーション内で使用するカード形式のUIコンポーネント。
    
    画像、タイトル、説明文を含むカードを表示します。クリック可能で、
    クリック時のコールバック関数を指定できます。
    
    Attributes:
        title (str): カードに表示するタイトル
        description (str): カードに表示する説明文
        image_url (str): カードの上部に表示する画像のURL
        on_click (Optional[Callable[[Any], None]]): カードがクリックされたときに呼び出されるコールバック関数
    """
    
    def __init__(
        self, 
        title: str, 
        description: str, 
        image_url: str, 
        on_click: Optional[Callable[[Any], None]] = None
    ) -> None:
        """AppCard インスタンスを初期化します。
        
        Args:
            title: カードに表示するタイトル
            description: カードに表示する説明文
            image_url: カードの上部に表示する画像のURL
            on_click: カードがクリックされたときに呼び出されるコールバック関数
        """
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url
        self.on_click = on_click

    def build(self) -> Card:
        """カードコンポーネントを構築します。
        
        Returns:
            Card: 構築されたカードコンポーネント
            
        Example:
            ```python
            # シンプルなカードの作成
            card = AppCard(
                title="サンプルタイトル",
                description="これはサンプルの説明文です。",
                image_url="https://example.com/image.jpg",
                on_click=lambda e: print("カードがクリックされました")
            )
            ```
        """
        return Card(
            elevation=4,
            content=Container(
                content=Column(
                    [
                        Image(
                            src=self.image_url,
                            width=float('inf'),
                            height=160,
                            fit=ImageFit.COVER,
                        ),
                        Container(
                            content=Column(
                                [
                                    Text(self.title, weight=FontWeight.BOLD, size=16),
                                    Text(
                                        self.description, size=14, color=colors.GREY_700
                                    ),
                                ]
                            ),
                            padding=padding.all(16),
                        ),
                    ]
                ),
                on_click=self.on_click,
            ),
        )
