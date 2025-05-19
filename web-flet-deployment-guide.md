# Python Flet - Web版アプリ開発・公開の詳細ガイド

このガイドではPython Fletを使ったWebアプリケーションの開発からデプロイまでの詳細な手順を説明します。各ステップを確認しながら進めることができます。

## 1. 開発環境のセットアップ

### 1.1 Python環境のセットアップ
- [ ] Python 3.7以上がインストールされていることを確認
  ```bash
  python --version
  ```
- [ ] 仮想環境を作成して有効化（推奨）
  ```bash
  python -m venv flet_web_env
  # Windows
  flet_web_env\Scripts\activate
  # macOS/Linux
  source flet_web_env/bin/activate
  ```

### 1.2 Fletのインストール
- [ ] pip経由でFletをインストール
  ```bash
  pip install flet
  ```
- [ ] インストールを確認
  ```bash
  pip list | grep flet
  ```

### 1.3 Webアプリ開発用の追加ツール（オプション）
- [ ] 開発サーバーの自動リロード用のwatchdogをインストール
  ```bash
  pip install watchdog
  ```
- [ ] Node.jsとnpmをインストール（Webリソースの最適化に役立つ）
  - [Node.js公式サイト](https://nodejs.org/)からダウンロード

## 2. Fletアプリケーションの開発

### 2.1 基本的なFlet Webアプリの作成
- [ ] 新しいプロジェクトディレクトリを作成
  ```bash
  mkdir my_flet_web_app
  cd my_flet_web_app
  ```
- [ ] メインアプリファイルを作成（`main.py`）:
  ```python
  import flet as ft

  def main(page: ft.Page):
      page.title = "My Flet Web App"
      page.theme_mode = ft.ThemeMode.LIGHT

      # レスポンシブ設定
      page.on_resize = page_resize

      # アプリの内容を追加
      page.add(
          ft.Text("Hello, Web from Python Flet!", size=20)
      )

  def page_resize(e):
      e.page.update()

  # Webアプリとして実行
  ft.app(target=main, view=ft.AppView.WEB_BROWSER)
  ```
- [ ] ローカルでアプリを実行してテスト
  ```bash
  python main.py
  ```

### 2.2 Web向けの最適化
- [ ] レスポンシブデザインの実装
  ```python
  def page_resize(e):
      # 画面サイズに応じたレイアウト調整
      if e.page.width < 600:
          # モバイルレイアウト
          e.page.padding = 10
      else:
          # デスクトップレイアウト
          e.page.padding = 20
      e.page.update()
  ```
- [ ] メタタグとSEO対策
  ```python
  page.web_meta = {
      "description": "あなたのアプリの説明",
      "keywords": "flet, python, web app",
      "author": "あなたの名前"
  }
  ```

### 2.3 ルーティングとナビゲーションの設定
- [ ] URLベースのルーティングを実装
  ```python
  def route_change(e):
      route = e.route if e.route else "/"

      if route == "/":
          page.views.clear()
          page.views.append(home_view())
      elif route == "/about":
          page.views.append(about_view())

      page.update()

  page.on_route_change = route_change
  ```

### 2.4 アセットの管理
- [ ] 静的ファイル用のディレクトリ構造を作成
  ```
  my_flet_web_app/
  ├── assets/
  │   ├── images/
  │   ├── fonts/
  │   └── styles/
  ├── main.py
  └── requirements.txt
  ```
- [ ] アセットの参照方法
  ```python
  page.add(
      ft.Image(src="/assets/images/logo.png", width=100, height=100)
  )
  ```

## 3. Webアプリのビルド

### 3.1 ビルド前の準備
- [ ] 依存パッケージが全てインストールされていることを確認
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] .gitignoreファイルの作成（不要なファイルを除外）
  ```
  __pycache__/
  *.py[cod]
  *$py.class
  venv/
  .env
  build/
  dist/
  ```
- [ ] 環境変数とconfigファイルの分離（開発/本番環境用）

### 3.2 静的Webアプリのビルド
- [ ] Flet CLIを使ってWebアプリをビルド
  ```bash
  flet build web --project-name "MyFletWebApp"
  ```
- [ ] ビルドが成功したことを確認（`build/web`に生成される）
- [ ] 生成されたファイルの構成を確認
  ```
  build/web/
  ├── index.html
  ├── assets/
  ├── manifest.json
  └── ...
  ```

### 3.3 ビルドオプションのカスタマイズ
- [ ] Webマニフェストの設定
  ```bash
  flet build web --web-renderer canvaskit --pwa
  ```
- [ ] ファビコンの設定
  ```bash
  flet build web --web-favicon path/to/favicon.png
  ```

### 3.4 ローカルでのテスト
- [ ] 簡易HTTPサーバーでビルド結果をテスト
  ```bash
  cd build/web
  python -m http.server 8000
  ```
- [ ] ブラウザで http://localhost:8000 にアクセス
- [ ] 異なるブラウザとデバイスでの動作確認
  - [ ] Chrome, Firefox, Safari, Edgeでのテスト
  - [ ] レスポンシブデザインのテスト（デスクトップ/タブレット/モバイル）

## 4. 静的ホスティングサービスへのデプロイ

### 4.1 GitHub Pagesへのデプロイ
- [ ] Gitリポジトリの作成とコードのプッシュ
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin https://github.com/yourusername/your-repo.git
  git push -u origin main
  ```
- [ ] GitHub Pages設定
  - [ ] リポジトリの「Settings」>「Pages」にアクセス
  - [ ] ソースとして「GitHub Actions」を選択
  - [ ] 静的サイト用のワークフローファイルを作成:
    ```yaml
    # .github/workflows/deploy.yml
    name: Deploy to GitHub Pages
    on:
      push:
        branches: [ main ]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - name: Set up Python
            uses: actions/setup-python@v2
            with:
              python-version: '3.10'
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install flet
          - name: Build web app
            run: flet build web
          - name: Deploy
            uses: peaceiris/actions-gh-pages@v3
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }}
              publish_dir: ./build/web
    ```
- [ ] デプロイの確認
  - [ ] Actions タブでワークフローの実行を確認
  - [ ] `https://yourusername.github.io/your-repo` でサイトを表示

### 4.2 Netlifyへのデプロイ
- [ ] Netlifyアカウントの作成（[netlify.com](https://www.netlify.com/)）
- [ ] Netlify CLIのインストール（オプション）
  ```bash
  npm install -g netlify-cli
  ```
- [ ] `netlify.toml`設定ファイルの作成
  ```toml
  [build]
    command = "pip install flet && flet build web"
    publish = "build/web"
  ```
- [ ] デプロイ方法:
  - **オプション1**: Netlify CLIでデプロイ
    ```bash
    netlify deploy --prod
    ```
  - **オプション2**: Netlifyサイトから手動デプロイ
    - [ ] Netlifyサイトにログイン
    - [ ] 「Sites」>「Add new site」>「Import an existing project」
    - [ ] GitHubなどからリポジトリを連携
    - [ ] ビルド設定の確認と保存
- [ ] デプロイされたURLを確認し、サイトが正しく表示されることを確認

### 4.3 Vercelへのデプロイ
- [ ] Vercelアカウントの作成（[vercel.com](https://vercel.com/)）
- [ ] Vercel CLIのインストール（オプション）
  ```bash
  npm install -g vercel
  ```
- [ ] `vercel.json`設定ファイルの作成
  ```json
  {
    "buildCommand": "pip install flet && flet build web",
    "outputDirectory": "build/web",
    "framework": null
  }
  ```
- [ ] デプロイ方法:
  - **オプション1**: Vercel CLIでデプロイ
    ```bash
    vercel
    ```
  - **オプション2**: Vercelサイトから手動デプロイ
    - [ ] Vercelサイトにログイン
    - [ ] 「New Project」をクリック
    - [ ] GitHubなどからリポジトリを連携
    - [ ] ビルド設定の確認と保存
- [ ] デプロイされたURLを確認し、サイトが正しく表示されることを確認

## 5. Pythonウェブサーバーとしてのデプロイ（バックエンド付き）

### 5.1 Herokuへのデプロイ
- [ ] Heroku CLIのインストール
  - [Heroku CLI公式サイト](https://devcenter.heroku.com/articles/heroku-cli)からインストール
- [ ] Herokuアカウントの作成とログイン
  ```bash
  heroku login
  ```
- [ ] `Procfile`の作成（Herokuに実行コマンドを指示）
  ```
  web: python main.py
  ```
- [ ] `requirements.txt`の作成
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] 環境変数の設定とポート対応
  ```python
  import os
  import flet as ft

  def main(page: ft.Page):
      # アプリケーションコード

  # サーバーモードで実行
  port = int(os.environ.get("PORT", 8080))
  ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port)
  ```
- [ ] Herokuアプリの作成とデプロイ
  ```bash
  heroku create my-flet-app
  git push heroku main
  ```
- [ ] 動作確認
  ```bash
  heroku open
  ```

### 5.2 AWS Elastic Beanstalkへのデプロイ
- [ ] AWS CLIとEB CLIのインストール
  ```bash
  pip install awscli awsebcli
  ```
- [ ] AWSアカウントの設定
  ```bash
  aws configure
  ```
- [ ] `requirements.txt`の確認
- [ ] Elastic Beanstalk用の設定ファイル作成
  ```
  # .ebextensions/01_flask.config
  option_settings:
    aws:elasticbeanstalk:container:python:
      WSGIPath: main.py
    aws:elasticbeanstalk:application:environment:
      PYTHONPATH: "/var/app/current"
  ```
- [ ] Elastic Beanstalkアプリの初期化とデプロイ
  ```bash
  eb init -p python-3.8 my-flet-app
  eb create my-flet-env
  ```
- [ ] デプロイ後のURLで動作確認

### 5.3 Google Cloud Runへのデプロイ
- [ ] Google Cloudアカウントとプロジェクトの設定
- [ ] gcloudコマンドラインツールのインストール
- [ ] Dockerfileの作成
  ```Dockerfile
  FROM python:3.10-slim

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  ENV PORT 8080

  CMD python main.py
  ```
- [ ] Cloud Runへのデプロイ
  ```bash
  gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/flet-app
  gcloud run deploy flet-app --image gcr.io/YOUR_PROJECT_ID/flet-app --platform managed
  ```
- [ ] デプロイ後のURLで動作確認

## 6. カスタムドメインとSSL設定

### 6.1 ドメイン名の取得
- [ ] ドメインレジストラ（Namecheap, Google Domains, GoDaddyなど）でドメイン名を購入
- [ ] ドメインの管理画面にアクセス

### 6.2 DNSレコードの設定
- [ ] ホスティングサービスのDNS設定指示に従う
  - GitHub Pages: `CNAME`または`A`レコード
  - Netlify: `CNAME`レコード
  - Vercel: `CNAME`レコード
  - Heroku: `CNAME`レコード
- [ ] DNSの伝播を待つ（最大48時間）

### 6.3 SSL/TLS証明書の設定
- [ ] 多くのホスティングサービスは自動的にSSLを提供
- [ ] 手動設定が必要な場合:
  - Let's Encryptを使用して無料の証明書を取得
  - 証明書を更新するためのcronジョブを設定

### 6.4 リダイレクトの設定
- [ ] HTTPからHTTPSへのリダイレクト設定
- [ ] www有無のリダイレクト設定

## 7. Webアプリの最適化

### 7.1 パフォーマンス最適化
- [ ] 画像の最適化と圧縮
- [ ] キャッシュヘッダーの設定
- [ ] ローディング表示の実装
  ```python
  page.splash = ft.Container(
      content=ft.ProgressRing(),
      alignment=ft.alignment.center
  )
  ```

### 7.2 PWA (Progressive Web App) 対応
- [ ] PWAとしてビルド
  ```bash
  flet build web --pwa
  ```
- [ ] マニフェストファイルのカスタマイズ
- [ ] サービスワーカーの設定

### 7.3 アクセス解析の設定
- [ ] Google Analyticsなどの解析ツールの統合

## 8. メンテナンスと更新

### 8.1 継続的インテグレーション/継続的デプロイ (CI/CD) の設定
- [ ] GitHub Actionsなどを使ったCI/CDパイプラインの構築
- [ ] 自動テストの実装

### 8.2 バックアップと復元の計画
- [ ] 定期的なバックアップの設定
- [ ] 障害発生時の復旧手順の作成

## トラブルシューティング

### ビルド関連の問題
- **エラー**: `Module not found`
  - **解決策**: `requirements.txt`の内容を確認、必要なモジュールをインストール

- **エラー**: `Port already in use`
  - **解決策**: 別のポートを指定するか、使用中のプロセスを終了

### デプロイ関連の問題
- **エラー**: `Failed to build dependencies`
  - **解決策**: ビルド環境のPython/pipバージョンを確認

- **エラー**: `Deployment failed`
  - **解決策**: ログを確認し、特定のエラーメッセージに基づいて対処

## 参考リソース

- [Flet公式ドキュメント](https://flet.dev/docs/)
- [Flet Webアプリの例](https://github.com/flet-dev/examples/)
- [Netlifyドキュメント](https://docs.netlify.com/)
- [Vercelドキュメント](https://vercel.com/docs)
- [Herokuドキュメント](https://devcenter.heroku.com/)

---

このガイドは基本的な手順を説明していますが、Fletや関連技術の更新により内容が変わる可能性があります。最新の情報は常に公式ドキュメントを参照してください。
