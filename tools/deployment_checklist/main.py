import flet as ft
import json
import os
import platform
from datetime import datetime
from pathlib import Path

def main(page: ft.Page):
    page.title = "Flet デプロイメントチェックリスト生成ツール"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # テーマ設定
    apply_app_theme(page)
    
    # プロジェクト情報
    project_name = ft.TextField(
        label="プロジェクト名",
        hint_text="例: My Flet App",
        width=500
    )
    
    project_description = ft.TextField(
        label="プロジェクト説明",
        hint_text="アプリの簡単な説明",
        width=500,
        multiline=True,
        min_lines=2,
        max_lines=4
    )
    
    # デプロイ先プラットフォーム
    deploy_targets = ft.Column([
        ft.Text("デプロイ先プラットフォーム", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Checkbox(label="Android", value=True),
            ft.Checkbox(label="iOS", value=True),
            ft.Checkbox(label="Web", value=True),
            ft.Checkbox(label="Windows", value=False),
            ft.Checkbox(label="macOS", value=False),
            ft.Checkbox(label="Linux", value=False),
        ]),
    ])
    
    # チェックリストの生成
    def generate_checklist(_):
        checklist_data = {
            "project_name": project_name.value or "Flet App",
            "project_description": project_description.value or "マルチプラットフォームFletアプリケーション",
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "platforms": []
        }
        
        # 選択されたプラットフォームを取得
        platforms = deploy_targets.controls[1].controls
        selected_platforms = []
        for platform_checkbox in platforms:
            if platform_checkbox.value:
                selected_platforms.append(platform_checkbox.label)
        
        # プラットフォーム別チェックリストを生成
        for platform_name in selected_platforms:
            platform_checklist = get_platform_checklist(platform_name)
            checklist_data["platforms"].append({
                "name": platform_name,
                "checklist": platform_checklist
            })
        
        # チェックリストをMarkdownで表示
        md_checklist = generate_markdown_checklist(checklist_data)
        checklist_preview.value = md_checklist
        
        # チェックリストをJSONにも保存
        json_path = Path(__file__).parent / "checklists" / f"{project_name.value or 'flet_app'}_checklist.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(checklist_data, f, ensure_ascii=False, indent=2)
        
        page.update()
      generate_button = ft.ElevatedButton(
        text="チェックリストを生成",
        on_click=generate_checklist,
        icon="checklist"
    )
    
    # チェックリストのプレビュー
    checklist_preview = ft.TextField(
        label="生成されたチェックリスト",
        multiline=True,
        min_lines=20,
        max_lines=30,
        read_only=True,
        width=900
    )
    
    # チェックリストのエクスポート
    def export_checklist(_):
        if not checklist_preview.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("チェックリストが生成されていません"))
            page.snack_bar.open = True
            page.update()
            return
            
        file_dialog = ft.FilePicker()
        page.overlay.append(file_dialog)
        
        def save_result(e: ft.FilePickerResultEvent):
            if e.path:
                try:
                    with open(e.path, "w", encoding="utf-8") as f:
                        f.write(checklist_preview.value)
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"チェックリストを {e.path} に保存しました"))
                    page.snack_bar.open = True
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"保存エラー: {str(ex)}"))
                    page.snack_bar.open = True
            page.update()
        
        file_dialog.on_result = save_result
        file_dialog.save_file(
            allowed_extensions=["md"],
            initial_filename=f"{project_name.value or 'flet_app'}_checklist.md"
        )
      export_button = ft.ElevatedButton(
        text="Markdownとして保存",
        icon="download",
        on_click=export_checklist
    )
    
    # レイアウト
    page.add(
        ft.AppBar(title=ft.Text("Flet デプロイメントチェックリスト生成ツール"), center_title=True),
        ft.Container(
            content=ft.Column([
                ft.Text("プロジェクト情報", size=20, weight=ft.FontWeight.BOLD),
                project_name,
                project_description,
                ft.Container(height=20),
                deploy_targets,
                ft.Container(height=10),
                generate_button,
                ft.Container(height=20),
                ft.Text("生成されたチェックリスト", size=20, weight=ft.FontWeight.BOLD),
                checklist_preview,
                export_button,
            ]),
            padding=20
        )
    )

def apply_app_theme(page: ft.Page):
    # 最新のFlet APIを使用してテーマを設定
    page.theme = ft.Theme(
        color_scheme_seed="blue",
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed="blue",
        use_material3=True,
    )

def get_platform_checklist(platform_name):
    """プラットフォーム別のチェックリストを取得"""
    # 共通のチェックリスト項目
    common_items = [
        {"id": "common_1", "text": "アプリの基本機能が正常に動作することを確認", "category": "機能テスト"},
        {"id": "common_2", "text": "レスポンシブデザインの検証", "category": "UI/UX"},
        {"id": "common_3", "text": "ダークモード/ライトモード両方での表示確認", "category": "UI/UX"},
        {"id": "common_4", "text": "アプリアイコンの準備", "category": "アセット"},
        {"id": "common_5", "text": "アプリバージョンの設定", "category": "設定"},
        {"id": "common_6", "text": "エラーハンドリングの実装確認", "category": "機能テスト"},
        {"id": "common_7", "text": "パフォーマンステスト", "category": "パフォーマンス"},
    ]
    
    # プラットフォーム固有のチェックリスト項目
    platform_items = {
        "Android": [
            {"id": "android_1", "text": "AndroidManifest.xmlの設定確認", "category": "設定"},
            {"id": "android_2", "text": "必要な権限の設定", "category": "設定"},
            {"id": "android_3", "text": "異なる画面サイズでのテスト", "category": "UI/UX"},
            {"id": "android_4", "text": "Google Play Store用のスクリーンショット準備", "category": "マーケティング"},
            {"id": "android_5", "text": "プライバシーポリシーの作成", "category": "法務"},
            {"id": "android_6", "text": "App Bundleの生成", "category": "ビルド"},
            {"id": "android_7", "text": "Google Play Console開発者アカウントの確認", "category": "配布"},
            {"id": "android_8", "text": "アプリ内課金の設定（必要な場合）", "category": "収益化"},
            {"id": "android_9", "text": "Firebase Crashlyticsの設定（オプション）", "category": "モニタリング"},
            {"id": "android_10", "text": "バックボタン処理の確認", "category": "UI/UX"},
        ],
        "iOS": [
            {"id": "ios_1", "text": "Info.plistの設定確認", "category": "設定"},
            {"id": "ios_2", "text": "必要な権限の設定とUsage Descriptionの追加", "category": "設定"},
            {"id": "ios_3", "text": "異なるiOSデバイスでのテスト", "category": "UI/UX"},
            {"id": "ios_4", "text": "App Store用のスクリーンショット準備", "category": "マーケティング"},
            {"id": "ios_5", "text": "プライバシーポリシーの作成", "category": "法務"},
            {"id": "ios_6", "text": "アーカイブの生成とApp Store Connectへのアップロード", "category": "ビルド"},
            {"id": "ios_7", "text": "Apple Developer Programの有効期限確認", "category": "配布"},
            {"id": "ios_8", "text": "In-App Purchaseの設定（必要な場合）", "category": "収益化"},
            {"id": "ios_9", "text": "App Store Connect上のアプリ情報入力", "category": "配布"},
            {"id": "ios_10", "text": "TestFlightを使ったベータテスト", "category": "テスト"},
        ],
        "Web": [
            {"id": "web_1", "text": "ブラウザ互換性テスト（Chrome, Firefox, Safari, Edge）", "category": "互換性"},
            {"id": "web_2", "text": "レスポンシブWebデザインの検証", "category": "UI/UX"},
            {"id": "web_3", "text": "ファビコンの設定", "category": "アセット"},
            {"id": "web_4", "text": "SEO対策（メタタグ、OGタグ）", "category": "マーケティング"},
            {"id": "web_5", "text": "Webアナリティクスの設定", "category": "モニタリング"},
            {"id": "web_6", "text": "サービスワーカーの設定（PWA対応）", "category": "機能"},
            {"id": "web_7", "text": "HTTPS対応の確認", "category": "セキュリティ"},
            {"id": "web_8", "text": "Webホスティングプラットフォームの選定", "category": "インフラ"},
            {"id": "web_9", "text": "ドメイン設定の確認", "category": "インフラ"},
            {"id": "web_10", "text": "ビルドサイズの最適化", "category": "パフォーマンス"},
        ],
        "Windows": [
            {"id": "windows_1", "text": "Windows 10/11での動作確認", "category": "互換性"},
            {"id": "windows_2", "text": "インストーラーパッケージの作成", "category": "配布"},
            {"id": "windows_3", "text": "MSIXパッケージの検討", "category": "配布"},
            {"id": "windows_4", "text": "Microsoft Storeへの登録検討", "category": "配布"},
            {"id": "windows_5", "text": "Windows通知システムとの連携", "category": "機能"},
            {"id": "windows_6", "text": "ショートカットキーの設定", "category": "UI/UX"},
            {"id": "windows_7", "text": "起動時間の最適化", "category": "パフォーマンス"},
            {"id": "windows_8", "text": "アンインストーラーの確認", "category": "配布"},
        ],
        "macOS": [
            {"id": "macos_1", "text": "最新macOSでの動作確認", "category": "互換性"},
            {"id": "macos_2", "text": "DMGインストーラーの作成", "category": "配布"},
            {"id": "macos_3", "text": "Apple公証（Notarization）", "category": "セキュリティ"},
            {"id": "macos_4", "text": "Mac App Storeへの登録検討", "category": "配布"},
            {"id": "macos_5", "text": "Dock対応の確認", "category": "UI/UX"},
            {"id": "macos_6", "text": "ショートカットキーの設定", "category": "UI/UX"},
            {"id": "macos_7", "text": "Touch Barサポート（対応機種の場合）", "category": "UI/UX"},
            {"id": "macos_8", "text": "ダークモード対応の確認", "category": "UI/UX"},
        ],
        "Linux": [
            {"id": "linux_1", "text": "主要ディストリビューション（Ubuntu, Fedora等）での動作確認", "category": "互換性"},
            {"id": "linux_2", "text": "Debパッケージの作成", "category": "配布"},
            {"id": "linux_3", "text": "AppImageの検討", "category": "配布"},
            {"id": "linux_4", "text": "Snapパッケージの検討", "category": "配布"},
            {"id": "linux_5", "text": "デスクトップエントリファイルの設定", "category": "設定"},
            {"id": "linux_6", "text": "GTK/Qtテーマとの調和", "category": "UI/UX"},
            {"id": "linux_7", "text": "ビルド依存関係の最小化", "category": "ビルド"},
            {"id": "linux_8", "text": "FlatpakでのSnapstoreへの対応検討", "category": "配布"},
        ]
    }
    
    # 共通項目と選択されたプラットフォーム固有の項目を結合
    return common_items + platform_items.get(platform_name, [])

def generate_markdown_checklist(checklist_data):
    """チェックリストデータからMarkdownを生成"""
    md = f"# {checklist_data['project_name']} デプロイメントチェックリスト\n\n"
    md += f"**プロジェクト説明**: {checklist_data['project_description']}\n\n"
    md += f"**生成日時**: {checklist_data['generated_date']}\n\n"
    
    for platform in checklist_data["platforms"]:
        md += f"## {platform['name']}\n\n"
        
        # カテゴリごとにグループ化
        categories = {}
        for item in platform["checklist"]:
            category = item["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # カテゴリごとにチェックリストを表示
        for category, items in categories.items():
            md += f"### {category}\n\n"
            for item in items:
                md += f"- [ ] {item['text']}\n"
            md += "\n"
    
    md += "## 共通リマインダー\n\n"
    md += "- [ ] すべてのプラットフォームでアプリが最終テストされていることを確認\n"
    md += "- [ ] リリースノートの作成\n"
    md += "- [ ] バックアップの作成\n"
    md += "- [ ] マーケティング計画の準備\n"
    md += "- [ ] サポート体制の準備\n\n"
    
    md += "## デプロイ後のタスク\n\n"
    md += "- [ ] アプリのパフォーマンス監視\n"
    md += "- [ ] ユーザーフィードバックの収集\n"
    md += "- [ ] クラッシュレポートの確認\n"
    md += "- [ ] ユーザー獲得の追跡\n"
    md += "- [ ] 次回アップデートの計画\n"
    
    return md

if __name__ == "__main__":
    ft.app(target=main)
