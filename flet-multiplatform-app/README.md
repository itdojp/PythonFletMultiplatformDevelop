# Flet Multiplatform App

このプロジェクトは、Python Fletを使用してマルチプラットフォーム対応のアプリケーションを開発するためのものです。Android、iOS、Webの各プラットフォームで一貫したユーザー体験を提供することを目的としています。

## プロジェクト構成

```
flet-multiplatform-app
├── src                     # アプリケーションのソースコード
│   ├── main.py            # アプリケーションのエントリーポイント
│   ├── app.py             # アプリケーションの主要なロジック
│   ├── utils               # ユーティリティ関数
│   │   ├── __init__.py
│   │   ├── platform_utils.py
│   │   └── responsive_utils.py
│   ├── config              # 設定ファイル
│   │   ├── __init__.py
│   │   └── theme_config.py
│   ├── components          # UIコンポーネント
│   │   ├── __init__.py
│   │   ├── common
│   │   │   ├── __init__.py
│   │   │   ├── app_card.py
│   │   │   ├── custom_buttons.py
│   │   │   └── loading_skeleton.py
│   │   ├── navigation
│   │   │   ├── __init__.py
│   │   │   ├── bottom_nav.py
│   │   │   └── side_nav.py
│   │   └── screens
│   │       ├── __init__.py
│   │       ├── home_screen.py
│   │       ├── settings_screen.py
│   │       └── profile_screen.py
│   ├── services            # サービス
│   │   ├── __init__.py
│   │   └── api_service.py
│   └── assets              # アセット
│       ├── fonts
│       └── icons
├── tests                   # テスト
│   ├── __init__.py
│   ├── test_components.py
│   └── test_responsive.py
├── docs                    # ドキュメント
│   └── design_guidelines.md
├── requirements.txt        # 依存関係
├── pyproject.toml         # プロジェクト設定
└── README.md               # プロジェクトの概要
```

## 使用方法

1. **依存関係のインストール**  
   プロジェクトのルートディレクトリで以下のコマンドを実行して、必要なパッケージをインストールします。
   ```
   pip install -r requirements.txt
   ```

2. **アプリケーションの起動**  
   `src/main.py`を実行してアプリケーションを起動します。
   ```
   python src/main.py
   ```

3. **テストの実行**  
   テストを実行するには、以下のコマンドを使用します。
   ```
   pytest tests/
   ```

## 貢献

このプロジェクトへの貢献は大歓迎です。バグの報告や機能の提案は、GitHubのイシューを通じて行ってください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。