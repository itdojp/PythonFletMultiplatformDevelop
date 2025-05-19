# Python Flet - Android版アプリ開発・公開の詳細ガイド

このガイドではPython Fletを使ったAndroidアプリケーションの開発から、Google Playストアへの公開までの詳細な手順を説明します。各ステップを確認しながら進めることができます。

## 1. 開発環境のセットアップ

### 1.1 Python環境のセットアップ
- [ ] Python 3.7以上がインストールされていることを確認
  ```bash
  python --version
  ```
- [ ] 仮想環境を作成して有効化（推奨）
  ```bash
  python -m venv flet_env
  # Windows
  flet_env\Scripts\activate
  # macOS/Linux
  source flet_env/bin/activate
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

### 1.3 Android開発環境のセットアップ
- [ ] [Flutter SDK](https://docs.flutter.dev/get-started/install)をダウンロードしてインストール
- [ ] 環境変数にFlutterのbinディレクトリを追加
- [ ] Flutterのインストールを確認
  ```bash
  flutter --version
  ```
- [ ] [Android Studio](https://developer.android.com/studio)をインストール
- [ ] Android SDKをインストール（Android Studioのセットアップ中に選択）
- [ ] Android SDKマネージャーから以下をインストール:
  - [ ] Android SDK Build-Tools
  - [ ] Android SDK Command-line Tools
  - [ ] Android SDK Platform-Tools
  - [ ] 対象Android APIレベル（APIレベル26以上推奨）
- [ ] Flutter doctorでセットアップを確認
  ```bash
  flutter doctor
  ```

## 2. Fletアプリケーションの開発

### 2.1 基本的なFletアプリの作成
- [ ] 新しいプロジェクトディレクトリを作成
  ```bash
  mkdir my_flet_app
  cd my_flet_app
  ```
- [ ] メインアプリファイルを作成（`main.py`）:
  ```python
  import flet as ft

  def main(page: ft.Page):
      page.title = "My Flet App"
      page.theme_mode = ft.ThemeMode.LIGHT

      # アプリの内容を追加
      page.add(
          ft.Text("Hello, Android from Python Flet!", size=20)
      )

  ft.app(target=main)
  ```
- [ ] アプリが動作するか確認
  ```bash
  python main.py
  ```

### 2.2 Android向けの最適化
- [ ] レスポンシブデザインの実装
  ```python
  def main(page: ft.Page):
      page.title = "My Flet App"

      # モバイル画面向けにパディングを調整
      page.padding = 10 if page.width < 600 else 20

      # レスポンシブコンテンツを追加
      # ...
  ```
- [ ] モバイル固有の機能対応
  ```python
  # プラットフォーム検出の例
  if page.platform == "android":
      # Android向け設定
      pass
  ```
- [ ] アプリアイコンの準備（推奨サイズ: 512x512ピクセル）
- [ ] スプラッシュスクリーンの準備

### 2.3 アプリの追加設定
- [ ] `pubspec.yaml`の作成またはカスタマイズ（Flutter設定用）
- [ ] `android/app/src/main/AndroidManifest.xml`の設定
  - [ ] 必要な権限の追加（インターネットアクセスなど）
  - [ ] アプリ名の設定
  - [ ] アイコンのパスの設定

## 3. Androidアプリのビルド

### 3.1 ビルド前の準備
- [ ] 依存パッケージが全てインストールされていることを確認
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] リソースファイル（画像、フォントなど）が正しく配置されていることを確認
- [ ] アプリケーションIDを決定（com.yourcompany.yourappname形式）

### 3.2 APKのビルド
- [ ] Flet CLIを使ってAndroidアプリをビルド
  ```bash
  flet build apk --project-name "MyFletApp" --package-name "com.yourcompany.yourappname"
  ```
- [ ] ビルドが成功したことを確認（`build/app/outputs/flutter-apk/app-release.apk`に生成される）

### 3.3 ビルドオプションのカスタマイズ
- [ ] アプリアイコンの指定
  ```bash
  flet build apk --icon path/to/icon.png
  ```
- [ ] バージョン情報の指定
  ```bash
  flet build apk --version "1.0.0" --build-number 1
  ```

### 3.4 APKのテスト
- [ ] エミュレータでテスト
  ```bash
  # エミュレータを起動
  flutter emulators --launch <emulator_id>
  # APKをインストール
  flutter install
  ```
- [ ] 実機でテスト（USBデバッグを有効にした実機を接続）
  ```bash
  adb install build/app/outputs/flutter-apk/app-release.apk
  ```
- [ ] 主要な機能が全て動作することを確認
- [ ] 異なる画面サイズでUIをテスト

## 4. Google Play Storeへの登録と公開

### 4.1 Google Playデベロッパーアカウントの設定
- [ ] [Google Play Console](https://play.google.com/console/signup)にアクセス
- [ ] デベロッパーアカウントを作成（$25の登録料）
- [ ] 必要な情報を入力（連絡先情報、支払い情報など）

### 4.2 プライバシーポリシーの作成
- [ ] プライバシーポリシーを作成（以下の項目を含める）:
  - [ ] 収集する情報の種類
  - [ ] 情報の使用方法
  - [ ] データ共有ポリシー
  - [ ] ユーザーの権利
  - [ ] 連絡先情報
- [ ] プライバシーポリシーをWebサイトに公開し、URLを取得

### 4.3 アプリの登録
- [ ] Google Play Consoleにログイン
- [ ] 「アプリの作成」を選択
- [ ] 基本情報を入力:
  - [ ] アプリ名
  - [ ] デフォルト言語
  - [ ] アプリタイプ（アプリ/ゲーム）
  - [ ] 無料/有料
  - [ ] カテゴリ

### 4.4 ストアの掲載情報の設定
- [ ] アプリの詳細情報を入力:
  - [ ] アプリの簡単な説明（80文字以内）
  - [ ] アプリの詳細な説明（4,000文字以内）
  - [ ] アプリアイコン（512x512ピクセル）
  - [ ] フィーチャーグラフィック（1024×500ピクセル）
- [ ] スクリーンショットをアップロード:
  - [ ] スマートフォン（最低2枚）: 16:9比率推奨
  - [ ] 7インチタブレット（オプション）
  - [ ] 10インチタブレット（オプション）
- [ ] プロモーション動画（オプション）

### 4.5 コンテンツレーティングの設定
- [ ] コンテンツレーティングの質問票に回答
- [ ] 対象年齢層を設定

### 4.6 APKのアップロード
- [ ] 「アプリリリース」セクションで「内部テスト」、「クローズドテスト」または「本番」を選択
- [ ] 新しいリリースを作成
- [ ] 署名付きAPKファイルをアップロード
- [ ] リリースノートを入力
- [ ] 保存してレビュー

### 4.7 価格と販売地域の設定
- [ ] アプリの価格設定（無料/有料）
- [ ] 販売する国と地域を選択

### 4.8 公開設定
- [ ] アプリのレビューを申請
- [ ] Googleの審査プロセスを待つ（通常数時間〜数日）
- [ ] アプリが承認されたら公開ステータスを確認

## 5. アプリのメンテナンスと更新

### 5.1 フィードバックとレビューの管理
- [ ] ユーザーレビューを定期的にチェック
- [ ] 問題に迅速に対応

### 5.2 アプリの更新
- [ ] バグ修正と新機能の実装
- [ ] 新しいバージョンのビルド
  ```bash
  flet build apk --version "1.0.1" --build-number 2
  ```
- [ ] Google Play Consoleで新しいリリースを作成
- [ ] 更新されたAPKをアップロード
- [ ] リリースノートを更新
- [ ] レビューと公開

## トラブルシューティング

### ビルド関連の問題
- **エラー**: `flutter not found`
  - **解決策**: FlutterのパスがPATH環境変数に正しく追加されているか確認

- **エラー**: `Gradle build failed`
  - **解決策**: Gradleバージョンの互換性を確認、インターネット接続を確認

- **エラー**: `SDK license not accepted`
  - **解決策**: `flutter doctor --android-licenses` を実行してライセンスに同意

### Google Play関連の問題
- **エラー**: `APK has not been signed`
  - **解決策**: 署名付きAPKを生成するためのキーストアを設定

- **エラー**: `App does not comply with policy XYZ`
  - **解決策**: Google Playポリシーをチェックして修正

## 参考リソース

- [Flet公式ドキュメント](https://flet.dev/docs/)
- [Flutter公式ドキュメント](https://docs.flutter.dev/)
- [Google Play Console ヘルプ](https://support.google.com/googleplay/android-developer/)
- [Flutter/Dart Cookbook](https://flutter.dev/docs/cookbook)

---

このガイドは基本的な手順を説明していますが、Fletや関連技術の更新により内容が変わる可能性があります。最新の情報は常に公式ドキュメントを参照してください。
