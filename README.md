# Flet Multiplatform Project Hub

## 概要

このリポジトリは、Fletフレームワークを使用したマルチプラットフォーム対応アプリケーションの開発基盤を提供するプロジェクトハブです。単一のコードベースからデスクトップ、ウェブ、モバイルアプリケーションを効率的に構築し、強力なPythonバックエンドAPI（FastAPIを利用）と連携させることを目的としています。

このプロジェクトは、開発者が迅速に高品質なマルチプラットフォームアプリケーションを立ち上げ、保守・拡張していく上での共通的な課題（開発環境の統一、UIとバックエンドの連携、CI/CDの整備など）を解決するためのテンプレート、ツール、ガイドラインを提供します。

## 主な特徴

-   **マルチプラットフォームGUI**: [Flet](https://flet.dev/) を使用し、Pythonのみでインタラクティブなフロントエンドを構築。Windows, macOS, Linux, Web, (将来的にはiOS/Android) に対応。
-   **強力なバックエンドAPI**: [FastAPI](https://fastapi.tiangolo.com/) を採用し、高性能でモダンな非同期APIを提供。
-   **開発支援ツール**: コーディング、テスト、デプロイメントを支援する各種ツールを同梱。
-   **CI/CDパイプライン**: GitHub Actionsを使用した継続的インテグレーションとデプロイメントのワークフローを定義済み。

## プロジェクト構造

このリポジトリは、複数のコンポーネントとドキュメントから構成されています。

-   `flet-multiplatform-app/`:
    主要なFlet GUIアプリケーションとFastAPIバックエンドAPIのソースコード、詳細なドキュメントが含まれています。このアプリケーションのセットアップ、開発、テストに関する詳細は、`flet-multiplatform-app/README.md` を参照してください。
-   `tools/`:
    開発効率を向上させるための各種スクリプトや補助ツール群が格納されています。詳細は `tools/README.md` を参照してください。
-   `.github/workflows/`:
    CI (継続的インテグレーション) および CD (継続的デプロイメント) のためのGitHub Actionsワークフロー定義ファイルが格納されています。
-   各種 `.md` ガイドファイル (ルートディレクトリ):
    リポジトリ全体に関わる横断的なガイドや、特定のプラットフォームへのデプロイメント手順などを記載したマークダウンファイル群です。

## 技術スタック

本プロジェクトで主に使用されている技術は以下の通りです。

-   **プログラミング言語**: Python 3.13+
-   **GUIフレームワーク**: Flet
-   **バックエンドAPIフレームワーク**: FastAPI
-   **非同期処理**: Uvicorn (ASGIサーバー), asyncio
-   **データベース (バックエンドAPI)**: SQLAlchemy (ORM), Alembic (マイグレーション) - (主に `flet-multiplatform-app` 内で使用)
-   **型チェック**: Pydantic (データバリデーションと設定管理)
-   **テスト**: Pytest, Pytest-Cov
-   **コードフォーマット・リンター**: Black, isort, Flake8, MyPy

(依存関係の詳細は各サブプロジェクトの `pyproject.toml` や `requirements.txt` を参照してください。)

## はじめに (Getting Started)

1.  **リポジトリのクローン:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```
    (上記URLは実際のリポジトリURLに置き換えてください)

2.  **メインアプリケーションのセットアップと起動:**
    主要なFletアプリケーション (`flet-multiplatform-app`) のセットアップ方法、開発環境の構築、アプリケーションの起動手順については、以下のドキュメントを参照してください。
    *   `flet-multiplatform-app/README.md`
    *   `flet-multiplatform-app/docs/getting_started.md` (日本語版は `GETTING_STARTED_JA.md`)

## ドキュメンテーション

このプロジェクトには、開発と運用を支援するための複数のドキュメントが用意されています。

-   **アプリケーション開発ドキュメント (`flet-multiplatform-app/docs/`)**:
    *   `DEVELOPER_GUIDE.md`: 開発環境のセットアップ、コーディング規約、コントリビューション方法など。
    *   `API_REFERENCE.md`: バックエンドAPIのエンドポイント仕様。
    *   `DESIGN_GUIDELINES.md`: UI/UXデザインに関する指針。
    *   `TUTORIAL.md`: アプリケーション機能開発のチュートリアル。
-   **デプロイメントガイド**:
    *   `android-flet-deployment-guide.md`: AndroidプラットフォームへのFletアプリケーションデプロイガイド。
    *   `ios-flet-deployment-guide.md`: iOSプラットフォームへのFletアプリケーションデプロイガイド。
    *   `web-flet-deployment-guide.md`: WebプラットフォームへのFletアプリケーションデプロイガイド。
-   **CI/CD & リリース**:
    *   `cicd-release-guide.md`: CI/CDパイプラインの概要とリリース手順。
-   **その他主要ガイド**:
    *   `architecture-design-guide.md`: プロジェクト全体のアーキテクチャ設計思想。
    *   `security-checklist.md`: セキュリティに関するチェックリスト。
    *   `testing-qa-guide.md`: テスト戦略と品質保証に関するガイド。

各ドキュメントは、それぞれの `.md` ファイルを参照してください。

## 貢献方法 (Contributing)

このプロジェクトへの貢献に興味がある方は、`flet-multiplatform-app/docs/DEVELOPER_GUIDE.md` に記載されている開発ワークフロー、コーディング規約、プルリクエストの手順などを参照してください。

バグ報告や機能提案は、GitHubのIssuesを通じて行うことを推奨します。

## ライセンス

このプロジェクトは MIT License の下で公開されています。詳細については、リポジトリ内の `LICENSE` ファイルを参照してください。もし `LICENSE` ファイルが存在しない場合は、プロジェクトオーナーにライセンス情報を確認してください。
