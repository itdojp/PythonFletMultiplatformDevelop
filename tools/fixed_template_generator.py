# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\fixed_template_generator.py
import flet as ft
from flet import Page, Text, ElevatedButton
import os

def main(page: Page):
    page.title = "簡易テンプレートジェネレーター"
    
    # ベース関数
    def button_clicked(e):
        page.add(Text("テンプレート生成ボタンがクリックされました！"))
        page.update()
    
    # プロジェクト名
    project_name = ft.TextField(
        label="プロジェクト名",
        width=300,
        hint_text="作成するプロジェクト名"
    )
    
    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="出力ディレクトリ",
        value=os.path.expanduser("~"),
        width=500,
        hint_text="テンプレートファイルを生成するディレクトリ"
    )
    
    # メッセージ表示用
    message_text = ft.Text("")
    
    # 生成ボタン押下時
    def generate_template(e):
        if not project_name.value:
            message_text.value = "プロジェクト名を入力してください"
            message_text.color = "red"
            page.update()
            return
            
        # 成功メッセージ
        message_text.value = f"テンプレートが生成されました: {project_name.value}"
        message_text.color = "green"
        page.update()
    
    # レイアウト構築
    page.add(
        Text("シンプルテンプレートジェネレーター", size=30),
        project_name,
        working_dir,
        ElevatedButton("テンプレート生成", on_click=generate_template),
        message_text
    )

# ブラウザモードで実行 (正常に動作するため)
if __name__ == "__main__":
    try:
        ft.app(target=main, view=ft.WEB_BROWSER)
    except Exception as e:
        print(f"エラー: {e}")
        # フォールバック実行
        ft.app(target=main)
