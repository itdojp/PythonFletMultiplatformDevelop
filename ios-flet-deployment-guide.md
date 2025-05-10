# Python Flet - iOS版アプリ開発・公開の詳細ガイド

このガイドではPython Fletを使ったiOSアプリケーションの開発からApp Storeへの公開までの詳細な手順を説明します。各ステップを確認しながら進めることができます。

**重要**: iOS向けアプリの開発には、macOSが搭載されたMac（MacBook、iMac、Mac miniなど）が必須です。WindowsやLinuxではiOSアプリをビルドできません。

## 1. 開発環境のセットアップ

### 1.1 macOS環境の確認
- [ ] macOS 11.0（Big Sur）以上がインストールされていることを確認
  ```bash
  sw_vers
  ```
- [ ] 十分なディスク容量があることを確認（最低30GB以上の空き容量を推奨）
  ```bash
  df -h
  ```

### 1.2 Xcodeのインストール
- [ ] [Mac App Store](https://apps.apple.com/jp/app/xcode/id497799835)から最新版のXcodeをインストール
- [ ] Xcodeを少なくとも一度起動し、利用規約に同意
- [ ] コマンドラインツールをインストール
  ```bash
  xcode-select --install
  ```
- [ ] Xcodeのバージョンを確認
  ```bash
  xcodebuild -version
  ```

### 1.3 Python環境のセットアップ
- [ ] Python 3.7以上がインストールされていることを確認
  ```bash
  python3 --version
  ```
- [ ] 仮想環境を作成して有効化（推奨）
  ```bash
  python3 -m venv flet_ios_env
  source flet_ios_env/bin/activate
  ```

### 1.4 Fletのインストール
- [ ] pip経由でFletをインストール
  ```bash
  pip install flet
  ```
- [ ] インストールを確認
  ```bash
  pip list | grep flet
  ```

### 1.5 Flutter SDKのインストール
- [ ] [Flutter公式サイト](https://flutter.dev/docs/get-started/install/macos)からFlutter SDKをダウンロード
- [ ] ダウンロードしたアーカイブを展開（例: `~/development`フォルダ内）
  ```bash
  mkdir -p ~/development
  cd ~/development
  unzip ~/Downloads/flutter_macos_*.zip
  ```
- [ ] PATHに追加
  ```bash
  export PATH="$PATH:$HOME/development/flutter/bin"
  ```
- [ ] `~/.zshrc`または`~/.bash_profile`にPATHを永続化
  ```bash
  echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zshrc
  source ~/.zshrc
  ```
- [ ] Flutterのインストールを確認
  ```bash
  flutter --version
  ```
- [ ] Flutterの依存関係をチェック
  ```bash
  flutter doctor
  ```

### 1.6 iOSシミュレータのセットアップ
- [ ] iOSシミュレータをインストール（Xcode経由）
  - Xcode > Preferences > Components > Simulators
- [ ] シミュレータを起動
  ```bash
  open -a Simulator
  ```

## 2. Apple Developer Programへの登録

### 2.1 Apple IDの準備
- [ ] [Apple ID](https://appleid.apple.com/)を持っていることを確認
- [ ] 2ファクタ認証が有効になっていることを確認

### 2.2 Apple Developer Programへの登録
- [ ] [Apple Developer Program](https://developer.apple.com/programs/)にアクセス
- [ ] 「Enroll」ボタンをクリック
- [ ] 年間$99（約14,000円）の登録料を支払う
- [ ] 必要な情報を入力:
  - [ ] 個人または企業/組織の選択
  - [ ] 連絡先情報
  - [ ] 税務情報
  - [ ] 支払い情報
- [ ] 審査プロセスを待つ（通常数日かかります）

### 2.3 開発者アカウントの確認
- [ ] [Apple Developer](https://developer.apple.com/)サイトにログイン
- [ ] ダッシュボードにアクセスして登録が完了していることを確認

## 3. Fletアプリケーションの開発

### 3.1 基本的なFletアプリの作成
- [ ] 新しいプロジェクトディレクトリを作成
  ```bash
  mkdir my_flet_ios_app
  cd my_flet_ios_app
  ```
- [ ] メインアプリファイルを作成（`main.py`）:
  ```python
  import flet as ft

  def main(page: ft.Page):
      page.title = "My Flet iOS App"
      page.theme_mode = ft.ThemeMode.LIGHT
      
      # アプリの内容を追加
      page.add(
          ft.Text("Hello, iOS from Python Flet!", size=20)
      )

  ft.app(target=main)
  ```
- [ ] アプリが動作するか確認
  ```bash
  python main.py
  ```

### 3.2 iOS向けの最適化
- [ ] レスポンシブデザインの実装
  ```python
  def main(page: ft.Page):
      page.title = "My Flet iOS App"
      
      # モバイル画面向けにパディングを調整
      page.padding = 10 if page.width < 600 else 20
      
      # iOSスタイルの要素を追加
      page.add(
          ft.AppBar(
              title=ft.Text("My iOS App"),
              center_title=False,
              bgcolor=ft.colors.BLUE_500,
              color=ft.colors.WHITE
          ),
          # その他の内容
      )
  ```
- [ ] iOSのジェスチャーとナビゲーションに対応
  ```python
  # スワイプジェスチャーの例
  def on_swipe(e):
      if e.direction == "right":
          # 右スワイプの処理
          pass
      
  container = ft.GestureDetector(
      on_horizontal_drag_end=on_swipe,
      content=ft.Container(
          content=ft.Text("Swipe me right"),
          padding=10
      )
  )
  page.add(container)
  ```

### 3.3 アプリアイコンとスプラッシュスクリーンの作成
- [ ] アプリアイコンの作成（推奨サイズ: 1024x1024ピクセル）
  - 様々な解像度のアイコンがiOS向けに必要になります
- [ ] スプラッシュスクリーンの作成（Light/Darkモード対応）

### 3.4 iOSの機能連携
- [ ] プラットフォーム固有の機能対応
  ```python
  # プラットフォーム検出の例
  if page.platform == "ios":
      # iOS向け設定
      pass
  ```

## 4. iPAファイルのビルド

### 4.1 ビルド前の準備
- [ ] 依存パッケージが全てインストールされていることを確認
  ```bash
  pip freeze > requirements.txt
  ```
- [ ] リソースファイル（画像、フォントなど）が正しく配置されていることを確認
- [ ] アプリケーションID（Bundleインデックス）を決定（com.yourcompany.yourappname形式）

### 4.2 アプリケーション設定
- [ ] `macos/Runner/Info.plist`のカスタマイズ
  - [ ] アプリ名の設定
  - [ ] バンドルIDの設定
  - [ ] バージョン情報の設定
  - [ ] 必要な権限の追加

### 4.3 コード署名の設定
- [ ] [Apple Developer Portal](https://developer.apple.com/account/)にアクセス
- [ ] 「Certificates, Identifiers & Profiles」セクションに移動
- [ ] アプリIDの作成:
  - [ ] 「Identifiers」>「+」ボタン
  - [ ] 「App IDs」を選択
  - [ ] 説明とBundle IDを入力
  - [ ] 必要な機能（Push通知など）を選択
  - [ ] 「Register」をクリック
- [ ] 証明書の作成:
  - [ ] 「Certificates」>「+」ボタン
  - [ ] 「iOS App Development」と「iOS Distribution」の両方を作成
  - [ ] 指示に従って証明書署名リクエスト（CSR）を生成
  - [ ] 生成された証明書をダウンロードして開く（自動的にKeychain Accessに追加される）
- [ ] プロビジョニングプロファイルの作成:
  - [ ] 「Profiles」>「+」ボタン
  - [ ] 「iOS App Development」（開発用）を選択
  - [ ] 先ほど作成したApp IDを選択
  - [ ] 使用する証明書を選択
  - [ ] テスト用デバイスを登録して選択
  - [ ] プロファイル名を入力して「Generate」をクリック
  - [ ] 生成されたプロビジョニングプロファイルをダウンロード

### 4.4 Xcodeプロジェクト設定
- [ ] FletプロジェクトからiOS向けのプロジェクトファイルを生成
  ```bash
  flet build ios --no-build
  ```
- [ ] Xcodeでプロジェクトを開く
  ```bash
  open ios/Runner.xcworkspace
  ```
- [ ] 「Signing & Capabilities」タブで以下を設定:
  - [ ] チーム（Apple Developer Accountに関連付けられたチーム）
  - [ ] Bundle Identifier（先ほど作成したものと一致させる）
  - [ ] プロビジョニングプロファイル（自動的に選択される）

### 4.5 iPAのビルド
- [ ] コマンドラインからiPAをビルド
  ```bash
  flet build ipa --bundle-identifier "com.yourcompany.yourappname" --build-number 1 --version "1.0.0"
  ```
- [ ] ビルドが成功したことを確認（`build/ios/ipa`に生成される）

### 4.6 シミュレータでのテスト
- [ ] iOSシミュレータでテスト
  ```bash
  # シミュレータを起動
  open -a Simulator
  # アプリをインストール（デバッグビルド）
  flutter run
  ```
- [ ] 様々なiOSデバイス（iPhone/iPad）と画面サイズでテスト
- [ ] 主要な機能が全て動作することを確認

### 4.7 実機でのテスト
- [ ] 実機にアプリをインストール:
  - [ ] デバイスをMacに接続
  - [ ] Xcodeでデバイスを選択して「Run」ボタンをクリック
  - [ ] または、Apple Configuratorを使用してiPAをインストール
- [ ] アプリが正常に動作することを確認

## 5. TestFlightでのテスト配布

### 5.1 App Store Connectの設定
- [ ] [App Store Connect](https://appstoreconnect.apple.com/)にログイン
- [ ] 「マイアプリ」>「＋」ボタンをクリック
- [ ] 新しいアプリを登録:
  - [ ] プラットフォーム（iOS）
  - [ ] アプリ名
  - [ ] 主要言語
  - [ ] Bundle ID（作成済みのものを選択）
  - [ ] SKU（独自の識別子）
  - [ ] ユーザーアクセス（フルアクセス）

### 5.2 アプリ情報の入力
- [ ] App Store Connectでアプリ情報を設定:
  - [ ] アプリアイコン（1024x1024ピクセル）
  - [ ] プライバシーポリシーURL
  - [ ] カテゴリ

### 5.3 TestFlightでの内部テスト
- [ ] App Store Connectの「TestFlight」タブに移動
- [ ] 「App Store」タブから「ビルド」セクションへ
- [ ] Transporter（旧Application Loader）またはXcodeでiPAをアップロード
  ```bash
  # Xcodeからアップロード
  xcodebuild -exportArchive -archivePath build/ios/archive/Runner.xcarchive -exportOptionsPlist exportOptions.plist -exportPath build/ios/ipa
  ```
- [ ] アップロードしたビルドの処理が完了するまで待つ（数分～数時間）
- [ ] ビルドが処理されたら、「TestFlight」タブで確認
- [ ] 内部テスターを追加:
  - [ ] 「テスター」タブ >「内部テスター」
  - [ ] App Store Connectのユーザーを追加または招待
- [ ] ビルドを内部テスト用に有効化

### 5.4 外部テスト（オプション）
- [ ] 外部テスターを設定:
  - [ ] 「テスター」タブ >「外部テスター」>「グループを追加」
  - [ ] グループ名と説明を入力
  - [ ] テスターのメールアドレスを追加
- [ ] TestFlightの外部テスト情報を設定:
  - [ ] テスト詳細（テストのフィードバック用メールアドレスなど）
  - [ ] ベータアプリの説明
  - [ ] ベータテストのための情報
- [ ] Appleの審査を受ける（外部テスト用に簡易的な審査があります）
- [ ] 審査が完了したら、外部テスターに招待メールを送信

### 5.5 テストフィードバックの収集と対応
- [ ] テスターからのフィードバックを収集
- [ ] 問題があれば修正し、新しいビルドをアップロード
- [ ] 繰り返しテスト

## 6. App Storeへの公開

### 6.1 App Storeの掲載情報の設定
- [ ] App Store Connect「App Store」タブで以下を設定:
  - [ ] アプリ名と小見出し
  - [ ] 説明文（4,000文字以内）
  - [ ] プロモーションテキスト（170文字以内）
  - [ ] キーワード
  - [ ] サポートURL
  - [ ] マーケティングURL（オプション）
- [ ] スクリーンショットをアップロード:
  - [ ] 6.5インチディスプレイ（iPhone 12 Pro Max, 13 Pro Maxなど）
  - [ ] 5.5インチディスプレイ（iPhone 8 Plus）
  - [ ] iPadディスプレイ（必要な場合）
- [ ] App Preview動画（オプション）
- [ ] アプリ内課金情報（該当する場合）

### 6.2 利用規約とレビュー情報
- [ ] 年齢区分の設定
- [ ] 著作権情報の入力
- [ ] App Reviewの連絡先情報
- [ ] レビュー用メモ（審査担当者向けの情報）
- [ ] デモアカウント情報（ログインが必要な場合）

### 6.3 リリース情報
- [ ] バージョンリリース設定:
  - [ ] 「審査後に自動で公開」または「手動で公開」
  - [ ] ファズービルドオプション（段階的なリリース）
- [ ] リリース日の設定（将来の日付も可能）

### 6.4 公開申請
- [ ] すべての情報が入力されていることを確認
- [ ] 「審査のために提出」ボタンをクリック
- [ ] Appleの審査プロセスを待つ（通常1～3日、複雑なアプリや特別な機能がある場合はそれ以上）

### 6.5 審査への対応
- [ ] 審査中に質問があれば、App Store Connectの通知を確認して回答
- [ ] 拒否された場合は理由を確認し、必要な修正を行って再提出
- [ ] 承認されたら、設定に応じて自動的に公開されるか、手動で公開操作を行う

## 7. リリース後の管理

### 7.1 ユーザーフィードバックのモニタリング
- [ ] App Store Connectの「ユーザー」セクションでレビューを確認
- [ ] App Analyticsでパフォーマンスメトリクスを確認

### 7.2 アプリのアップデート
- [ ] バグ修正と新機能の実装
- [ ] 新しいバージョンのビルド
  ```bash
  flet build ipa --build-number <増加した番号> --version "<新しいバージョン>"
  ```
- [ ] App Store Connectで新しいバージョンを作成
- [ ] TestFlightでテスト
- [ ] App Storeに再提出

### 7.3 iOSの新バージョンへの対応
- [ ] 新しいiOSバージョンがリリースされたらテスト
- [ ] 必要に応じて更新をリリース

## トラブルシューティング

### ビルド関連の問題
- **エラー**: `Code Signing Error`
  - **解決策**: プロビジョニングプロファイルとチーム設定を確認

- **エラー**: `Missing Provisioning Profile`
  - **解決策**: 正しいプロビジョニングプロファイルをダウンロードし、Xcodeに追加

- **エラー**: `iOS Deployment Target is set to 8.0, but the range of supported deployment target version for this platform is 9.0 to 16.0`
  - **解決策**: プロジェクト設定でDeployment Targetを最新の互換バージョンに更新

### App Store関連の問題
- **エラー**: `iTunes Connect: Invalid Binary`
  - **解決策**: ビルド設定やアプリケーション識別子を確認

- **エラー**: `New apps and app updates must be built with the iOS 16.0 SDK or later`
  - **解決策**: XcodeとFlutterを最新バージョンに更新

- **問題**: `App Rejected - Guideline X.Y`
  - **解決策**: Appleのガイドラインを確認し、指摘された問題を修正

## 参考リソース

- [Flet公式ドキュメント](https://flet.dev/docs/)
- [Flutter iOS開発ガイド](https://flutter.dev/docs/deployment/ios)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [TestFlight Beta Testing](https://developer.apple.com/testflight/)

---

このガイドは基本的な手順を説明していますが、Fletや関連技術の更新により内容が変わる可能性があります。最新の情報は常に公式ドキュメントを参照してください。