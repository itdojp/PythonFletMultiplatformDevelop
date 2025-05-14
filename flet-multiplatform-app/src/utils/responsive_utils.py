"""レスポンシブデザインを実現するためのユーティリティ関数を提供するモジュール。

このモジュールは、画面サイズに応じてレイアウトを動的に調整するための関数を提供します。
主にモバイル、タブレット、デスクトップの3つのブレークポイントをサポートしています。
"""

import flet as ft
from typing import Any, Literal

# ブレークポイントの型定義
BreakpointType = Literal["mobile", "tablet", "desktop"]

def get_breakpoint(page_width: float) -> BreakpointType:
    """画面の幅に基づいて現在のブレークポイントを返します。
    
    Args:
        page_width: 画面の幅（ピクセル単位）
        
    Returns:
        BreakpointType: 現在のブレークポイント（"mobile", "tablet", "desktop"のいずれか）
        
    Example:
        ```python
        # 画面幅が500pxの場合
        breakpoint = get_breakpoint(500)  # "mobile" を返す
        
        # 画面幅が800pxの場合
        breakpoint = get_breakpoint(800)  # "tablet" を返す
        
        # 画面幅が1200pxの場合
        breakpoint = get_breakpoint(1200)  # "desktop" を返す
        ```
    """
    if page_width < 600:
        return "mobile"
    elif page_width < 960:
        return "tablet"
    else:
        return "desktop"


def adjust_layout_for_responsive_design(page: Any) -> None:
    """画面サイズに基づいてページのレイアウトを調整します。
    
    この関数は、画面サイズに応じて以下の調整を行います：
    - モバイル（幅 < 600px）: 中央揃え、幅90%
    - タブレット（600px <= 幅 < 960px）: 左揃え、幅70%
    - デスクトップ（幅 >= 960px）: 左揃え、固定幅800px
    
    Args:
        page: FletのPageオブジェクト
        
    Example:
        ```python
        import flet as ft
        from utils.responsive_utils import adjust_layout_for_responsive_design
        
        def main(page: ft.Page):
            # ページの設定
            page.title = "Responsive App"
            
            # ウィンドウサイズ変更時のコールバックを設定
            def on_resize(e):
                adjust_layout_for_responsive_design(page)
                
            page.on_resize = on_resize
            
            # 初期レイアウトを適用
            adjust_layout_for_responsive_design(page)
            
            # コンテンツを追加
            page.add(
                ft.Text("Responsive Layout Example"),
                ft.ElevatedButton("Click me")
            )
            
        ft.app(target=main)
        ```
    """
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
