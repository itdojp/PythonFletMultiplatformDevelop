# Python Flet - マルチプラットフォームUI/UXデザインガイドライン

このガイドラインは、Python Fletを使用して開発するアプリケーションにおいて、Android、iOS、Webの各プラットフォームで一貫性のある優れたユーザー体験を提供するための指針を提供します。

> **関連ガイド**:
> - [プラットフォーム共通コード管理ガイド](./cross-platform-code-management-guide.md) - レスポンシブデザインとアダプティブUIの実装
> - [アーキテクチャ設計ガイド](./architecture-design-guide.md) - コンポーネント設計と状態管理
> - [Androidデプロイガイド](./android-flet-deployment-guide.md) - Androidプラットフォーム固有の考慮事項

## 目次

1. [デザイン原則](#デザイン原則)
2. [レスポンシブデザイン](#レスポンシブデザイン)
3. [プラットフォーム固有のガイドライン](#プラットフォーム固有のガイドライン)
4. [コンポーネント設計](#コンポーネント設計)
5. [テーマとスタイリング](#テーマとスタイリング)
6. [アクセシビリティ](#アクセシビリティ)
7. [パフォーマンスとUX](#パフォーマンスとux)
8. [Fletコード実装例](#fletコード実装例)

## デザイン原則

Fletアプリケーションを設計する際の基本原則:

### 一貫性
- [ ] 全プラットフォームで一貫した用語、アイコン、操作パターンを使用する
- [ ] アプリケーション全体で統一されたデザイン言語を維持する
- [ ] 一貫したカラーパレットとタイポグラフィを適用する

### シンプルさ
- [ ] ユーザーインターフェースは必要最小限の要素で構成する
- [ ] 各画面の主要な目的を明確にし、余分な情報を排除する
- [ ] 直感的な操作フローを設計する

### フィードバック
- [ ] ユーザーアクションに対して適切な視覚的フィードバックを提供する
- [ ] 処理時間が長い操作にはプログレスインジケーターを表示する
- [ ] エラー状態には明確なエラーメッセージと解決方法を示す

### フォーカス
- [ ] 重要なコンテンツや操作に視覚的な優先順位を付ける
- [ ] 情報の階層構造を明確にする
- [ ] ユーザーの注意を最も重要なタスクに集中させる

## レスポンシブデザイン

マルチプラットフォーム対応のための重要な柱:

### 適応型レイアウト
- [ ] 様々な画面サイズに対応するフレキシブルなレイアウトを設計する
- [ ] ブレークポイントを設定して異なる画面サイズに最適化する
  ```python
  def page_resize(e):
      # スマートフォン
      if e.page.width < 600:
          e.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
          for control in e.page.controls:
              control.width = e.page.width * 0.9
      # タブレット
      elif e.page.width < 960:
          e.page.horizontal_alignment = ft.CrossAxisAlignment.START
          for control in e.page.controls:
              control.width = e.page.width * 0.7
      # デスクトップ
      else:
          e.page.horizontal_alignment = ft.CrossAxisAlignment.START
          for control in e.page.controls:
              control.width = 800
      e.page.update()
  ```

### 適応型コンテンツ
- [ ] テキストサイズを相対単位で指定し、読みやすさを維持する
- [ ] 画像とメディアを異なる解像度に対応させる
- [ ] コンテンツの優先順位付けを行い、小さな画面では重要な要素のみ表示する

### レイアウトパターン
- [ ] スタック/リスト: 垂直方向にコンテンツを積み重ねる基本パターン
  ```python
  page.add(
      ft.Column([
          ft.Text("項目1"),
          ft.Text("項目2"),
          ft.Text("項目3")
      ])
  )
  ```
- [ ] グリッド: 空間効率の高いデータ表示
  ```python
  page.add(
      ft.GridView(
          expand=True,
          max_extent=150,
          child_aspect_ratio=1.0,
          spacing=10,
          run_spacing=10,
          children=[
              ft.Container(
                  content=ft.Text(f"項目 {i}"),
                  alignment=ft.alignment.center,
                  bgcolor=ft.colors.BLUE_100,
              ) for i in range(20)
          ]
      )
  )
  ```
- [ ] マスター/詳細: 一覧と詳細の2ペイン構造（画面サイズに応じて1画面または2画面に分割）

## プラットフォーム固有のガイドライン

### Android (Material Design)
- [ ] マテリアルデザインの原則に従う
- [ ] FAB（フローティングアクションボタン）を主要アクションに使用
  ```python
  page.add(
      ft.FloatingActionButton(
          icon=ft.icons.ADD,
          on_click=add_item
      )
  )
  ```
- [ ] マテリアルアイコンセットを使用
- [ ] ボトムナビゲーションバーを主要ナビゲーションに使用
  ```python
  page.add(
      ft.NavigationBar(
          destinations=[
              ft.NavigationDestination(icon=ft.icons.HOME, label="ホーム"),
              ft.NavigationDestination(icon=ft.icons.SEARCH, label="検索"),
              ft.NavigationDestination(icon=ft.icons.PERSON, label="プロフィール")
          ]
      )
  )
  ```

### iOS (Human Interface Guidelines)
- [ ] iOSのHIGに準拠したデザイン
- [ ] タブバーを主要ナビゲーションに使用
  ```python
  # iOS風のタブバー
  page.add(
      ft.Tabs(
          selected_index=0,
          tabs=[
              ft.Tab(text="ホーム", icon=ft.icons.HOME),
              ft.Tab(text="検索", icon=ft.icons.SEARCH),
              ft.Tab(text="設定", icon=ft.icons.SETTINGS)
          ]
      )
  )
  ```
- [ ] モーダルシートを補助的な情報表示やアクションに使用
- [ ] iOS風の詳細な表示トランジションを実装

### Web
- [ ] レスポンシブWebデザインの原則に従う
- [ ] デスクトップではサイドナビゲーション、モバイルではハンバーガーメニューを使用
  ```python
  # レスポンシブなナビゲーション
  def build_navigation(page):
      if page.width < 600:
          # モバイル用ハンバーガーメニュー
          return ft.AppBar(
              title=ft.Text("アプリ名"),
              leading=ft.IconButton(icon=ft.icons.MENU, on_click=open_drawer)
          )
      else:
          # デスクトップ用サイドナビゲーション
          return ft.NavigationRail(
              selected_index=0,
              destinations=[
                  ft.NavigationRailDestination(icon=ft.icons.HOME, label="ホーム"),
                  ft.NavigationRailDestination(icon=ft.icons.SEARCH, label="検索"),
                  ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="設定")
              ]
          )
  ```
- [ ] プログレッシブ・エンハンスメントを適用（基本機能を確保した上で、対応デバイスには高度な機能を提供）
- [ ] Webアクセシビリティ基準（WCAG）に準拠

## コンポーネント設計

### 共通コンポーネント
- [ ] ボタン: プライマリ、セカンダリ、テキストの3種類を一貫して使用
  ```python
  # ボタンのスタイル統一
  def primary_button(text, on_click):
      return ft.ElevatedButton(text=text, on_click=on_click, style=ft.ButtonStyle(
          color=ft.colors.WHITE,
          bgcolor=ft.colors.BLUE_500,
          padding=10,
      ))

  def secondary_button(text, on_click):
      return ft.OutlinedButton(text=text, on_click=on_click, style=ft.ButtonStyle(
          color=ft.colors.BLUE_500,
          padding=10,
      ))

  def text_button(text, on_click):
      return ft.TextButton(text=text, on_click=on_click, style=ft.ButtonStyle(
          color=ft.colors.BLUE_500,
      ))
  ```
- [ ] カード: 関連情報をグループ化する一貫したカードコンポーネント
- [ ] フォーム要素: 統一されたスタイルのテキスト入力、セレクター、チェックボックスなど
- [ ] ダイアログ: 一貫したアラート、確認、入力ダイアログ

### カスタムコンポーネント
- [ ] 再利用可能なカスタムコンポーネントの設計
  ```python
  class UserCard(ft.UserControl):
      def __init__(self, name, role, avatar_url):
          super().__init__()
          self.name = name
          self.role = role
          self.avatar_url = avatar_url

      def build(self):
          return ft.Card(
              content=ft.Container(
                  content=ft.Column([
                      ft.CircleAvatar(foreground_image_url=self.avatar_url),
                      ft.Text(self.name, weight=ft.FontWeight.BOLD),
                      ft.Text(self.role, italic=True, size=12)
                  ]),
                  padding=10
              )
          )

  # 使用例
  page.add(UserCard("山田太郎", "開発者", "https://example.com/avatar.jpg"))
  ```
- [ ] プラットフォーム間で一貫したコンポーネントライブラリの構築
- [ ] デザイントークン（色、間隔、タイポグラフィなど）を使用した設計システムの確立

## テーマとスタイリング

### カラーパレット
- [ ] ブランドカラーを定義（プライマリカラー、セカンダリカラー）
- [ ] 補完的な色（アクセントカラー）
- [ ] グレースケールの段階
- [ ] 意味的な色（成功、警告、エラーなど）
  ```python
  # アプリ全体のテーマカラー設定
  def main(page: ft.Page):
      page.theme = ft.Theme(
          color_scheme=ft.ColorScheme(
              primary=ft.colors.BLUE_500,
              primary_container=ft.colors.BLUE_100,
              secondary=ft.colors.ORANGE_400,
              error=ft.colors.RED_500,
              background=ft.colors.WHITE,
          )
      )
  ```

### タイポグラフィ
- [ ] 見出し、本文、キャプションなどの一貫したフォントスタイル
- [ ] 読みやすさを優先したフォントサイズと行間
- [ ] プラットフォーム最適化（iOSではSan Francisco、AndroidではRobotoなど）
  ```python
  # テキストスタイルの定義
  heading_1 = ft.TextStyle(size=24, weight=ft.FontWeight.BOLD)
  heading_2 = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
  body_text = ft.TextStyle(size=16)
  caption = ft.TextStyle(size=12, italic=True)

  # 使用例
  page.add(
      ft.Text("見出し", style=heading_1),
      ft.Text("サブ見出し", style=heading_2),
      ft.Text("本文テキスト", style=body_text),
      ft.Text("キャプション", style=caption)
  )
  ```

### ダークモード
- [ ] ライト/ダークモードの両方をサポート
- [ ] 各モードで読みやすさとコントラストを確保
  ```python
  # ダークモード対応
  def main(page: ft.Page):
      page.theme_mode = ft.ThemeMode.SYSTEM  # システム設定に従う

      # ライトモードテーマ
      light_theme = ft.Theme(
          color_scheme=ft.ColorScheme(
              primary=ft.colors.BLUE_500,
              background=ft.colors.WHITE,
              # その他のカラー設定
          )
      )

      # ダークモードテーマ
      dark_theme = ft.Theme(
          color_scheme=ft.ColorScheme(
              primary=ft.colors.BLUE_300,  # ダークモードでは明るめの青
              background=ft.colors.GREY_900,
              # その他のカラー設定
          )
      )

      page.theme = light_theme
      page.dark_theme = dark_theme
  ```

## アクセシビリティ

### 基本原則
- [ ] 十分なコントラスト比（WCAG AAレベル以上）
- [ ] キーボード操作のサポート
- [ ] スクリーンリーダー対応
- [ ] フォーカス可視化

### Fletでの実装
- [ ] セマンティックラベルの提供
  ```python
  ft.IconButton(
      icon=ft.icons.SETTINGS,
      tooltip="設定",  # スクリーンリーダー用の説明
  )
  ```
- [ ] タッチターゲットの十分なサイズ確保（最低44x44dp）
- [ ] アクセシビリティテストとフィードバックの収集

## パフォーマンスとUX

### 読み込み最適化
- [ ] スケルトンスクリーンやプレースホルダーの使用
  ```python
  # スケルトンローディング
  def create_skeleton():
      return ft.Column([
          ft.Container(height=20, width=200, bgcolor=ft.colors.GREY_300, border_radius=4),
          ft.Container(height=20, width=150, bgcolor=ft.colors.GREY_300, border_radius=4, margin=ft.margin.only(top=8)),
          ft.Container(height=20, width=180, bgcolor=ft.colors.GREY_300, border_radius=4, margin=ft.margin.only(top=8)),
      ])

  # データ読み込み中はスケルトン表示
  loading = True
  content = create_skeleton() if loading else actual_content
  page.add(content)
  ```
- [ ] 遅延読み込みと段階的表示
- [ ] パフォーマンスメトリクスの測定と最適化

### インタラクション設計
- [ ] タッチジェスチャーの適切な実装（タップ、スワイプ、ピンチなど）
- [ ] トランジションとアニメーションの適切な使用
  ```python
  # アニメーションの例
  container = ft.Container(
      width=100,
      height=100,
      bgcolor=ft.colors.BLUE,
      border_radius=ft.border_radius.all(4),
      animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
  )

  def animate_container(e):
      container.width = 200 if container.width == 100 else 100
      container.bgcolor = ft.colors.RED if container.bgcolor == ft.colors.BLUE else ft.colors.BLUE
      container.update()

  page.add(
      container,
      ft.ElevatedButton("アニメーション", on_click=animate_container)
  )
  ```
- [ ] エラー状態と空の状態の適切な処理

## Fletコード実装例

### 共通テーマの適用
```python
def apply_app_theme(page: ft.Page):
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE_500,
            primary_container=ft.colors.BLUE_100,
            secondary=ft.colors.ORANGE_400,
            error=ft.colors.RED_500,
            background=ft.colors.WHITE,
        ),
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE_300,
            primary_container=ft.colors.BLUE_900,
            secondary=ft.colors.ORANGE_300,
            error=ft.colors.RED_300,
            background=ft.colors.GREY_900,
        ),
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        use_material3=True,
    )
    page.theme_mode = ft.ThemeMode.SYSTEM
```

### レスポンシブレイアウト
```python
def create_responsive_layout(page: ft.Page, content):
    def page_resize(e):
        if page.width < 600:
            # モバイルレイアウト
            layout.horizontal = False
            navbar.rail = False
            for item in content:
                item.col = None
                item.expand = True
        else:
            # デスクトップレイアウト
            layout.horizontal = True
            navbar.rail = True
            for i, item in enumerate(content):
                item.col = {i: i % 2 + 1 for i in range(len(content))}
                item.expand = True
        page.update()

    navbar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.HOME_OUTLINED, selected_icon=ft.icons.HOME, label="ホーム"),
            ft.NavigationRailDestination(icon=ft.icons.BOOKMARK_BORDER, selected_icon=ft.icons.BOOKMARK, label="保存"),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="設定"),
        ],
        rail=True,
    )

    layout = ft.Row([navbar, ft.Column(content, expand=True)], expand=True)

    page.on_resize = page_resize
    return layout
```

### クロスプラットフォームUIコンポーネント
```python
class AppCard(ft.UserControl):
    def __init__(self, title, description, image_url, on_click=None):
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url
        self.on_click = on_click

    def build(self):
        return ft.Card(
            elevation=4,
            content=ft.Container(
                content=ft.Column([
                    ft.Image(
                        src=self.image_url,
                        width=double.infinity,
                        height=160,
                        fit=ft.ImageFit.COVER,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(self.title, weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(self.description, size=14, color=ft.colors.GREY_700),
                        ]),
                        padding=ft.padding.all(16),
                    ),
                ]),
                on_click=self.on_click,
            )
        )
```

### プラットフォーム検出とUI調整
```python
def get_platform_specific_ui(page: ft.Page):
    if page.platform == "android":
        # Android向けのUI
        return ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_item)
    elif page.platform == "ios":
        # iOS向けのUI
        return ft.IconButton(icon=ft.icons.ADD, on_click=add_item)
    else:
        # Web向けのUI
        return ft.ElevatedButton("追加", on_click=add_item)
```

このガイドラインを参考に、各プラットフォームで一貫性があり、かつそれぞれのプラットフォームの特性を活かした優れたUI/UXを実現してください。Fletの力を借りて、Python一つでマルチプラットフォーム対応の美しいアプリケーションを構築しましょう。
