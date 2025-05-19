# Python Flet - アプリ分析・モニタリングガイド

このガイドでは、Python Fletで開発したマルチプラットフォームアプリケーションにおける分析・モニタリングの実装について解説します。ユーザー行動の追跡、パフォーマンス監視、クラッシュレポートの収集など、アプリの改善に必要なデータを効率的に収集・分析する方法を学びましょう。

## 目次

1. [分析・モニタリングの概要](#分析・モニタリングの概要)
2. [Firebase Analyticsの統合](#firebase-analyticsの統合)
3. [クラッシュレポートの収集](#クラッシュレポートの収集)
4. [パフォーマンスモニタリング](#パフォーマンスモニタリング)
5. [カスタムイベントの追跡](#カスタムイベントの追跡)
6. [ユーザーセグメント分析](#ユーザーセグメント分析)
7. [A/Bテストの実装](#abテストの実装)
8. [リモート構成（Remote Config）](#リモート構成remote-config)
9. [プライバシーとコンプライアンス](#プライバシーとコンプライアンス)
10. [分析データの活用](#分析データの活用)

## 分析・モニタリングの概要

アプリケーションの分析とモニタリングは、品質向上とユーザー満足度の改善に不可欠です。以下の重要な側面について解説します。

### 分析・モニタリングの目的

- **ユーザー行動の理解**: どの機能がよく使われているか、ユーザーの行動パターンを把握
- **パフォーマンスの最適化**: アプリの応答性やリソース使用状況を監視し改善
- **安定性の向上**: クラッシュやエラーを特定し修正
- **ユーザーエンゲージメントの向上**: ユーザーの好みやニーズに基づいて機能を改善
- **ビジネス意思決定の支援**: データに基づいた開発判断を下す

### 主要なメトリクス

1. **ユーザーメトリクス**
   - アクティブユーザー数（DAU/MAU）
   - 新規ユーザー率
   - リテンション率（継続利用率）
   - セッション長・頻度

2. **パフォーマンスメトリクス**
   - 起動時間
   - レスポンス時間
   - メモリ使用量
   - ネットワークリクエスト効率
   - バッテリー消費量

3. **安定性メトリクス**
   - クラッシュ率
   - ANR（Application Not Responding）発生率
   - エラー発生率
   - バージョン別の安定性傾向

4. **ビジネスメトリクス**
   - コンバージョン率
   - 目標達成率
   - 機能使用頻度
   - 購入・課金行動（該当する場合）

### クロスプラットフォームの課題と対策

Fletアプリケーションのような、マルチプラットフォーム環境での分析には特有の課題があります:

1. **プラットフォーム間の一貫性**:
   - 共通の分析体系を設計
   - プラットフォーム固有のメトリクスと共通メトリクスを区別
   - イベント名やパラメータを標準化

2. **データの統合と比較**:
   - 単一のダッシュボードでクロスプラットフォームデータを表示
   - プラットフォーム間でのユーザー行動の違いを分析

3. **効率的な実装**:
   - 分析コードを共通モジュールに集約
   - プラットフォーム固有の実装を最小限に

## Firebase Analyticsの統合

Firebase Analyticsは、マルチプラットフォームアプリに適した統合分析ソリューションです。Fletアプリケーションに統合する方法を解説します。

### 前提条件

- Firebaseプロジェクトの作成
- 各プラットフォーム（Android、iOS、Web）の設定

### インストールと基本設定

#### 1. 必要なパッケージのインストール

```bash
pip install flet firebase-admin
```

#### 2. Firebase Admin SDKの初期化

```python
# app/services/analytics_service.py
import firebase_admin
from firebase_admin import credentials, analytics

class AnalyticsService:
    def __init__(self):
        self.initialized = False
        try:
            # Firebase資格情報の初期化
            cred = credentials.Certificate('path/to/firebase-adminsdk.json')
            firebase_admin.initialize_app(cred)
            self.initialized = True
        except Exception as e:
            print(f"Firebase初期化エラー: {e}")

    def log_event(self, event_name, params=None):
        """イベントをログに記録"""
        if not self.initialized:
            print("Firebase Analyticsが初期化されていません")
            return

        try:
            # ここでFirebase AnalyticsにイベントをログJ
            print(f"イベントログ: {event_name}, パラメータ: {params}")
        except Exception as e:
            print(f"イベントログエラー: {e}")
```

#### 3. HTMLへのFirebase JS SDKの追加（Webアプリ用）

WebアプリとしてデプロイするFletアプリの場合、HTMLテンプレートを拡張して Firebase JS SDKを追加します。

```html
<!-- web/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fletアプリ</title>
    <!-- Firebase JS SDK -->
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.6.1/firebase-analytics.js"></script>
    <script>
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "YOUR_AUTH_DOMAIN",
            projectId: "YOUR_PROJECT_ID",
            storageBucket: "YOUR_STORAGE_BUCKET",
            messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
            appId: "YOUR_APP_ID",
            measurementId: "YOUR_MEASUREMENT_ID"
        };

        // Firebaseの初期化
        firebase.initializeApp(firebaseConfig);
        const analytics = firebase.analytics();
    </script>
</head>
<body>
    <!-- Fletアプリのコンテンツ -->
</body>
</html>
```

#### 4. プラットフォーム固有の設定

**Android** (`android/app/build.gradle`):

```gradle
dependencies {
    // 他の依存関係...
    implementation 'com.google.firebase:firebase-analytics:20.0.2'
}

apply plugin: 'com.google.gms.google-services'
```

**iOS** (`ios/Runner/Info.plist`):

```xml
<key>FirebaseAppDelegateProxyEnabled</key>
<true/>
```

### 分析サービスの実装

Fletアプリケーションで分析サービスを使用するための抽象化レイヤーを作成します：

```python
# app/services/analytics.py
import platform
from enum import Enum
import json
import os
import logging

logger = logging.getLogger(__name__)

class EventType(Enum):
    """トラッキングイベントの種類"""
    APP_OPEN = "app_open"
    SCREEN_VIEW = "screen_view"
    BUTTON_CLICK = "button_click"
    FEATURE_USE = "feature_use"
    ERROR = "error"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class AnalyticsService:
    """クロスプラットフォーム分析サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.platform = platform.system()
        self.enabled = self._check_analytics_enabled()

        # ローカルイベントキャッシュ
        self.event_cache = []
        self.max_cache_size = 100

        # プラットフォーム固有の初期化
        if self.platform == "Android":
            self._init_android()
        elif self.platform == "Darwin":  # macOS/iOS
            self._init_ios()
        else:
            self._init_web()

    def _check_analytics_enabled(self):
        """ユーザーが分析を有効にしているか確認"""
        # 設定ファイルから分析の有効/無効を読み込む
        # 実際の実装では、ユーザー設定やローカルストレージから読み込む
        try:
            return True  # デフォルトで有効
        except Exception as e:
            logger.error(f"分析設定の読み込みエラー: {e}")
            return False

    def _init_android(self):
        """Androidプラットフォーム固有の初期化"""
        logger.info("Android分析の初期化")
        # 実際の実装では、JNIを通じてAndroidのFirebase SDKを呼び出す

    def _init_ios(self):
        """iOSプラットフォーム固有の初期化"""
        logger.info("iOS分析の初期化")
        # 実際の実装では、ctypesを通じてiOSのFirebase SDKを呼び出す

    def _init_web(self):
        """Webプラットフォーム固有の初期化"""
        logger.info("Web分析の初期化")
        # 実際の実装では、JSからFirebase SDKを呼び出す

    def log_event(self, event_type, name=None, params=None):
        """イベントをログに記録"""
        if not self.enabled:
            return

        # イベント名の標準化
        if name is None:
            event_name = event_type.value
        else:
            event_name = f"{event_type.value}_{name}"

        # イベントパラメータの設定
        event_params = params or {}

        # プラットフォーム情報の追加
        event_params["platform"] = self.platform

        try:
            # プラットフォーム固有のログ記録
            if self.platform == "Android":
                self._log_android_event(event_name, event_params)
            elif self.platform == "Darwin":
                self._log_ios_event(event_name, event_params)
            else:
                self._log_web_event(event_name, event_params)

            # イベントをキャッシュに追加
            self._cache_event(event_name, event_params)

            logger.debug(f"イベントログ: {event_name}, パラメータ: {event_params}")
        except Exception as e:
            logger.error(f"イベントログエラー: {e}")

    def _log_android_event(self, event_name, params):
        """Androidプラットフォーム向けのイベントログ"""
        # 実際の実装
        pass

    def _log_ios_event(self, event_name, params):
        """iOSプラットフォーム向けのイベントログ"""
        # 実際の実装
        pass

    def _log_web_event(self, event_name, params):
        """Webプラットフォーム向けのイベントログ"""
        # 実際の実装: JavaScriptの分析関数を呼び出す
        pass

    def _cache_event(self, event_name, params):
        """イベントをローカルにキャッシュ"""
        self.event_cache.append({
            "name": event_name,
            "params": params,
            "timestamp": int(time.time() * 1000)
        })

        # キャッシュサイズを制限
        if len(self.event_cache) > self.max_cache_size:
            self.event_cache.pop(0)

    def flush(self):
        """キャッシュされたイベントを強制送信"""
        # 実際の実装ではバッチ処理でサーバーに送信
        logger.info("キャッシュされたイベントをフラッシュしました")
        self.event_cache = []

    def set_user_id(self, user_id):
        """ユーザーIDを設定"""
        if not self.enabled:
            return

        try:
            # 各プラットフォームでユーザーIDを設定
            logger.debug(f"ユーザーID設定: {user_id}")
        except Exception as e:
            logger.error(f"ユーザーID設定エラー: {e}")

    def set_user_property(self, name, value):
        """ユーザープロパティを設定"""
        if not self.enabled:
            return

        try:
            # 各プラットフォームでユーザープロパティを設定
            logger.debug(f"ユーザープロパティ設定: {name}={value}")
        except Exception as e:
            logger.error(f"ユーザープロパティ設定エラー: {e}")

    def set_enabled(self, enabled):
        """分析の有効/無効を切り替え"""
        self.enabled = enabled
        logger.info(f"分析サービス: {'有効' if enabled else '無効'}")
```

### アプリページでの利用例

```python
# app/pages/home_page.py
import flet as ft
from app.services.analytics import AnalyticsService, EventType

class HomePage(ft.Page):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.analytics = AnalyticsService()

        # 画面表示イベントをログに記録
        self.analytics.log_event(
            EventType.SCREEN_VIEW,
            name="home_page"
        )

        # UIコンポーネントの初期化
        self.init_ui()

    def init_ui(self):
        # UIコンポーネントの作成
        title = ft.Text("ホーム画面", size=20, weight="bold")

        btn_feature1 = ft.ElevatedButton(
            text="機能1を使用",
            on_click=self.use_feature1
        )

        # コンポーネントをページに追加
        self.page.add(title, btn_feature1)

    def use_feature1(self, e):
        # 機能1の実装

        # 機能使用イベントをログに記録
        self.analytics.log_event(
            EventType.FEATURE_USE,
            name="feature1",
            params={
                "source": "home_page",
                "mode": "standard"
            }
        )
```

## クラッシュレポートの収集

アプリケーションのクラッシュや例外を収集して分析することで、問題を迅速に特定し修正できます。

### Firebase Crashlyticsの設定

#### 1. Googleサービスの構成ファイル設置

- Android: `android/app/google-services.json`
- iOS: `ios/Runner/GoogleService-Info.plist`

#### 2. Crashlytics Pythonクライアントの実装

```python
# app/services/crash_reporter.py
import logging
import traceback
import platform
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class CrashReporter:
    """クラッシュレポート収集サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(CrashReporter, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.platform = platform.system()
        self.enabled = True
        self.reports_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "crash-reports")

        # 保存ディレクトリの作成
        os.makedirs(self.reports_dir, exist_ok=True)

        # 未送信のレポートを処理
        self._process_unsent_reports()

        # グローバル例外ハンドラの設定
        self._set_exception_handlers()

    def _set_exception_handlers(self):
        """グローバルな例外ハンドラを設定"""
        # メインスレッドの例外ハンドラ
        sys.excepthook = self._handle_exception

        # サブスレッドの例外ハンドラ
        original_thread_run = threading.Thread.run

        def patched_thread_run(self, *args, **kwargs):
            try:
                original_thread_run(self, *args, **kwargs)
            except Exception:
                crash_reporter = CrashReporter()
                crash_reporter._handle_exception(*sys.exc_info())

        threading.Thread.run = patched_thread_run

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """例外を処理してレポートを作成"""
        if not self.enabled:
            # デフォルトのハンドラに委譲
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        try:
            # スタックトレースを取得
            stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # クラッシュレポートの作成
            report = {
                "timestamp": int(time.time() * 1000),
                "platform": self.platform,
                "os_version": platform.version(),
                "device_model": platform.machine(),
                "app_version": getattr(sys.modules['__main__'], "__version__", "unknown"),
                "exception_type": exc_type.__name__,
                "exception_message": str(exc_value),
                "stack_trace": stack_trace,
                "python_version": sys.version
            }

            # レポートの保存と送信
            self._save_report(report)
            self._send_report(report)

            logger.error(f"アプリケーションクラッシュ: {exc_type.__name__}: {exc_value}")
        except Exception as e:
            logger.error(f"クラッシュレポート作成中にエラーが発生: {e}")

        # デフォルトのハンドラに委譲
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def _save_report(self, report):
        """レポートをローカルに保存"""
        try:
            report_id = f"{int(time.time() * 1000)}_{hash(str(report))}"
            report_path = os.path.join(self.reports_dir, f"{report_id}.json")

            with open(report_path, 'w') as f:
                json.dump(report, f)

            logger.debug(f"クラッシュレポート保存: {report_path}")
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")

    def _send_report(self, report):
        """レポートをサーバーに送信"""
        try:
            # 実際の実装では非同期にサーバーに送信
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self._upload_report, report)
        except Exception as e:
            logger.error(f"レポート送信エラー: {e}")

    def _upload_report(self, report):
        """レポートをサーバーにアップロード"""
        try:
            # 実際の実装では適切なAPIエンドポイントに送信
            logger.debug(f"クラッシュレポート送信: {report['exception_type']}")

            # 送信成功後、ローカルファイルを削除
            # self._remove_report(report_id)
        except Exception as e:
            logger.error(f"レポートアップロードエラー: {e}")

    def _process_unsent_reports(self):
        """未送信のレポートを処理"""
        try:
            for filename in os.listdir(self.reports_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.reports_dir, filename)

                    with open(file_path, 'r') as f:
                        report = json.load(f)

                    # 非同期に送信
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        executor.submit(self._upload_report, report)
        except Exception as e:
            logger.error(f"未送信レポート処理エラー: {e}")

    def log_non_fatal_exception(self, exception, additional_data=None):
        """致命的でない例外をログに記録"""
        if not self.enabled:
            return

        try:
            # 現在のスタックトレースを取得
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_traceback is None:  # 例外がスローされていない場合
                stack = traceback.extract_stack()[:-1]  # 現在の位置を除外
                stack_trace = ''.join(traceback.format_list(stack))
            else:
                stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

            # レポートの作成
            report = {
                "timestamp": int(time.time() * 1000),
                "platform": self.platform,
                "os_version": platform.version(),
                "device_model": platform.machine(),
                "app_version": getattr(sys.modules['__main__'], "__version__", "unknown"),
                "exception_type": exception.__class__.__name__,
                "exception_message": str(exception),
                "stack_trace": stack_trace,
                "is_fatal": False,
                "additional_data": additional_data,
                "python_version": sys.version
            }

            # レポートの送信
            self._send_report(report)

            logger.warning(f"非致命的例外: {exception.__class__.__name__}: {exception}")
        except Exception as e:
            logger.error(f"非致命的例外レポートエラー: {e}")

    def set_enabled(self, enabled):
        """クラッシュレポートの有効/無効を切り替え"""
        self.enabled = enabled
        logger.info(f"クラッシュレポート: {'有効' if enabled else '無効'}")

    def set_user_identifier(self, user_id):
        """ユーザー識別子を設定"""
        # 実際の実装ではFirebase CrashlyticsにユーザーIDを設定
        logger.debug(f"クラッシュレポートユーザーID設定: {user_id}")

    def set_custom_key(self, key, value):
        """カスタムキーを設定"""
        # 実際の実装ではFirebase Crashlyticsにカスタムキーを設定
        logger.debug(f"クラッシュレポートカスタムキー設定: {key}={value}")
```

### クラッシュレポーターの使用例

```python
# app/main.py
import flet as ft
from app.services.crash_reporter import CrashReporter

def main():
    # アプリケーション起動時にクラッシュレポーターを初期化
    crash_reporter = CrashReporter()

    def on_app_exception(e):
        """アプリケーション例外ハンドラ"""
        # 非致命的な例外をログに記録
        crash_reporter.log_non_fatal_exception(
            e,
            additional_data={"context": "app_initialization"}
        )

    try:
        # アプリケーションのメイン処理
        ft.app(target=init_app)
    except Exception as e:
        on_app_exception(e)
        raise  # 例外を再スロー

def init_app(page: ft.Page):
    # アプリケーションの初期化
    page.title = "Fletアプリ"

    try:
        # UIコンポーネントの初期化
        # ...

        # 意図的なクラッシュ（テスト用）
        if page.route == "/crash":
            raise Exception("テストクラッシュ")

    except Exception as e:
        # クラッシュレポーターですでにキャプチャされるため、
        # ここでの処理は最小限にする
        page.add(ft.Text(f"エラーが発生しました: {str(e)}"))

if __name__ == "__main__":
    main()
```

## パフォーマンスモニタリング

アプリケーションのパフォーマンスを監視して、ボトルネックを特定し最適化するための実装方法を解説します。

### パフォーマンスモニタリングサービスの実装

```python
# app/services/performance.py
import time
import logging
import platform
import threading
import psutil
import gc
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)

class TraceType(Enum):
    """トレースの種類"""
    NETWORK = "network"
    RENDER = "render"
    FUNCTION = "function"
    DATABASE = "database"
    STARTUP = "startup"
    CUSTOM = "custom"

class PerformanceMonitor:
    """パフォーマンスモニタリングサービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(PerformanceMonitor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.platform = platform.system()
        self.enabled = True

        # アクティブトレースの追跡
        self.active_traces = {}

        # パフォーマンスデータの保存
        self.metrics_history = {
            "cpu": deque(maxlen=100),
            "memory": deque(maxlen=100),
            "render_time": deque(maxlen=100),
            "network_time": deque(maxlen=100)
        }

        # バックグラウンド監視スレッドの開始
        self._start_background_monitoring()

    def _start_background_monitoring(self):
        """バックグラウンド監視スレッドを開始"""
        def monitor_resources():
            while self.enabled:
                try:
                    self._collect_system_metrics()
                    time.sleep(5)  # 5秒ごとに収集
                except Exception as e:
                    logger.error(f"リソース監視エラー: {e}")
                    time.sleep(10)  # エラー時は間隔を長くする

        # デーモンスレッドとして実行
        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()

    def _collect_system_metrics(self):
        """システムメトリクスを収集"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)

            # メモリ使用率
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)  # MBに変換

            # Pythonガベージコレクション統計
            gc_counts = gc.get_count()

            # メトリクスを記録
            timestamp = int(time.time() * 1000)

            self.metrics_history["cpu"].append({
                "timestamp": timestamp,
                "value": cpu_percent
            })

            self.metrics_history["memory"].append({
                "timestamp": timestamp,
                "value": memory_mb,
                "gc_counts": gc_counts
            })

            # ログに記録（デバッグ用）
            logger.debug(f"システムメトリクス - CPU: {cpu_percent}%, メモリ: {memory_mb:.2f}MB")
        except Exception as e:
            logger.error(f"メトリクス収集エラー: {e}")

    def start_trace(self, trace_type, name):
        """パフォーマンストレースを開始"""
        if not self.enabled:
            return None

        trace_id = f"{trace_type.value}_{name}_{int(time.time() * 1000)}"

        self.active_traces[trace_id] = {
            "type": trace_type.value,
            "name": name,
            "start_time": time.time(),
            "attributes": {},
            "counters": {}
        }

        return trace_id

    def stop_trace(self, trace_id):
        """パフォーマンストレースを終了して結果を記録"""
        if not self.enabled or trace_id not in self.active_traces:
            return None

        trace = self.active_traces.pop(trace_id)
        trace["end_time"] = time.time()
        trace["duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000

        # トレース種類に応じた処理
        trace_type = trace["type"]
        duration_ms = trace["duration_ms"]

        if trace_type == TraceType.RENDER.value:
            self.metrics_history["render_time"].append({
                "timestamp": int(time.time() * 1000),
                "value": duration_ms,
                "name": trace["name"]
            })
        elif trace_type == TraceType.NETWORK.value:
            self.metrics_history["network_time"].append({
                "timestamp": int(time.time() * 1000),
                "value": duration_ms,
                "name": trace["name"]
            })

        # 結果をログに記録
        logger.debug(f"パフォーマンストレース: {trace['name']} ({trace_type}) - {duration_ms:.2f}ms")

        return trace

    def add_trace_attribute(self, trace_id, key, value):
        """トレースに属性を追加"""
        if not self.enabled or trace_id not in self.active_traces:
            return

        self.active_traces[trace_id]["attributes"][key] = value

    def increment_trace_counter(self, trace_id, counter, increment=1):
        """トレースのカウンターを増加"""
        if not self.enabled or trace_id not in self.active_traces:
            return

        trace = self.active_traces[trace_id]
        if counter not in trace["counters"]:
            trace["counters"][counter] = 0

        trace["counters"][counter] += increment

    def record_metric(self, name, value):
        """カスタムメトリクスを記録"""
        if not self.enabled:
            return

        if name not in self.metrics_history:
            self.metrics_history[name] = deque(maxlen=100)

        self.metrics_history[name].append({
            "timestamp": int(time.time() * 1000),
            "value": value
        })

        logger.debug(f"カスタムメトリクス: {name} = {value}")

    def get_metrics(self, metric_name, limit=10):
        """指定されたメトリクスの履歴を取得"""
        if metric_name not in self.metrics_history:
            return []

        # 最新のN個のメトリクスを取得
        metrics = list(self.metrics_history[metric_name])[-limit:]
        return metrics

    def get_summary(self):
        """パフォーマンスメトリクスのサマリーを取得"""
        summary = {}

        for metric_name, metrics in self.metrics_history.items():
            if not metrics:
                continue

            values = [m["value"] for m in metrics]

            summary[metric_name] = {
                "current": values[-1] if values else None,
                "avg": sum(values) / len(values) if values else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "count": len(values)
            }

        return summary

    def set_enabled(self, enabled):
        """パフォーマンスモニタリングの有効/無効を切り替え"""
        self.enabled = enabled
        logger.info(f"パフォーマンスモニタリング: {'有効' if enabled else '無効'}")

# デコレータの実装
def trace(trace_type=TraceType.FUNCTION):
    """関数のパフォーマンスを追跡するデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            trace_id = monitor.start_trace(trace_type, func.__name__)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                if trace_id:
                    monitor.stop_trace(trace_id)

        return wrapper

    return decorator
```

### コンテキストマネージャーの実装

```python
# app/services/performance_context.py
from app.services.performance import PerformanceMonitor, TraceType
import time

class TraceContext:
    """パフォーマンストレースのためのコンテキストマネージャー"""

    def __init__(self, trace_type, name):
        self.trace_type = trace_type
        self.name = name
        self.monitor = PerformanceMonitor()
        self.trace_id = None

    def __enter__(self):
        self.trace_id = self.monitor.start_trace(self.trace_type, self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.trace_id:
            self.monitor.stop_trace(self.trace_id)

    def add_attribute(self, key, value):
        """トレースに属性を追加"""
        if self.trace_id:
            self.monitor.add_trace_attribute(self.trace_id, key, value)

    def increment_counter(self, counter, increment=1):
        """トレースのカウンターをインクリメント"""
        if self.trace_id:
            self.monitor.increment_trace_counter(self.trace_id, counter, increment)
```

### パフォーマンスモニタリングの使用例

```python
# app/pages/complex_page.py
import flet as ft
import time
import requests
from app.services.performance import trace, TraceType, PerformanceMonitor
from app.services.performance_context import TraceContext

class ComplexPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.monitor = PerformanceMonitor()

        # ページの初期化
        self.init_page()

    @trace(TraceType.RENDER)
    def init_page(self):
        """ページの初期化（デコレータを使用した追跡）"""
        self.page.title = "複雑なページ"

        # 複雑なUIコンポーネントの作成
        container = ft.Container(
            width=400,
            height=600,
            padding=10,
            content=ft.Column([
                ft.Text("複雑なページ", size=24, weight="bold"),
                self.create_data_section(),
                ft.ElevatedButton("データ更新", on_click=self.load_data)
            ])
        )

        self.page.add(container)

    def create_data_section(self):
        """データセクションを作成"""
        self.data_grid = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("名前")),
                ft.DataColumn(ft.Text("値"))
            ],
            rows=[]
        )

        return ft.Column([
            ft.Text("データセクション", size=18),
            self.data_grid,
            ft.ProgressBar(visible=False)
        ])

    async def load_data(self, e):
        """データを読み込む（コンテキストマネージャーを使用した追跡）"""
        # プログレスバーを表示
        progress_bar = self.page.controls[0].content.controls[1].controls[2]
        progress_bar.visible = True
        await self.page.update_async()

        with TraceContext(TraceType.NETWORK, "load_data") as trace:
            # データ取得の開始
            start_time = time.time()

            # 外部APIからデータを取得
            try:
                response = requests.get("https://api.example.com/data")
                data = response.json()

                # トレースに属性を追加
                trace.add_attribute("data_count", len(data))
                trace.add_attribute("status_code", response.status_code)

                # データテーブルを更新
                self.update_data_table(data)
            except Exception as e:
                print(f"データ取得エラー: {e}")
                # トレースにエラー情報を追加
                trace.add_attribute("error", str(e))

            # 処理時間をカスタムメトリクスとして記録
            elapsed_time = time.time() - start_time
            self.monitor.record_metric("data_load_time", elapsed_time * 1000)

        # プログレスバーを非表示
        progress_bar.visible = False
        await self.page.update_async()

    @trace(TraceType.RENDER)
    def update_data_table(self, data):
        """データテーブルを更新"""
        # 既存の行をクリア
        self.data_grid.rows.clear()

        # 新しい行を追加
        for item in data[:10]:  # 最初の10項目のみ表示
            self.data_grid.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item["id"]))),
                        ft.DataCell(ft.Text(item["name"])),
                        ft.DataCell(ft.Text(str(item["value"])))
                    ]
                )
            )
```

### パフォーマンスダッシュボードの実装

```python
# app/pages/performance_dashboard.py
import flet as ft
from app.services.performance import PerformanceMonitor

class PerformanceDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.monitor = PerformanceMonitor()

        # ダッシュボードの初期化
        self.init_dashboard()

    def init_dashboard(self):
        """ダッシュボードの初期化"""
        self.page.title = "パフォーマンスダッシュボード"

        # メトリクスカード
        self.cpu_card = self.create_metric_card("CPU使用率", "cpu", "%")
        self.memory_card = self.create_metric_card("メモリ使用量", "memory", "MB")
        self.render_time_card = self.create_metric_card("レンダリング時間", "render_time", "ms")
        self.network_time_card = self.create_metric_card("ネットワーク時間", "network_time", "ms")

        # 更新ボタン
        update_button = ft.ElevatedButton("更新", on_click=self.update_dashboard)

        # メトリクスグラフ
        self.cpu_graph = self.create_metric_graph("CPU使用率")
        self.memory_graph = self.create_metric_graph("メモリ使用量")

        # レイアウト
        self.page.add(
            ft.Text("パフォーマンスダッシュボード", size=24, weight="bold"),
            ft.Row([
                self.cpu_card,
                self.memory_card,
                self.render_time_card,
                self.network_time_card
            ]),
            update_button,
            ft.Row([
                self.cpu_graph,
                self.memory_graph
            ])
        )

        # 初回更新
        self.update_dashboard(None)

    def create_metric_card(self, title, metric_name, unit):
        """メトリクスカードを作成"""
        return ft.Card(
            content=ft.Container(
                width=200,
                height=120,
                padding=10,
                content=ft.Column([
                    ft.Text(title, size=16, weight="bold"),
                    ft.Row([
                        ft.Text("現在:", size=14),
                        ft.Text("--", size=14, weight="bold")
                    ]),
                    ft.Row([
                        ft.Text("平均:", size=14),
                        ft.Text("--", size=14)
                    ]),
                    ft.Row([
                        ft.Text("最大:", size=14),
                        ft.Text("--", size=14)
                    ]),
                    ft.Text(f"単位: {unit}", size=12, color="grey")
                ])
            )
        )

    def create_metric_graph(self, title):
        """メトリクスグラフを作成"""
        return ft.Container(
            width=400,
            height=300,
            padding=10,
            border=ft.border.all(1, "grey"),
            border_radius=5,
            content=ft.Column([
                ft.Text(title, size=16, weight="bold"),
                ft.Text("グラフ領域", size=14)
                # 実際のアプリでは、Fletのグラフコンポーネントを使用
            ])
        )

    def update_dashboard(self, e):
        """ダッシュボードを更新"""
        # パフォーマンスサマリーを取得
        summary = self.monitor.get_summary()

        # カードを更新
        self.update_metric_card(self.cpu_card, summary.get("cpu", {}))
        self.update_metric_card(self.memory_card, summary.get("memory", {}))
        self.update_metric_card(self.render_time_card, summary.get("render_time", {}))
        self.update_metric_card(self.network_time_card, summary.get("network_time", {}))

        # グラフを更新（実際のアプリでは実装する）

        # ページを更新
        self.page.update()

    def update_metric_card(self, card, metric_data):
        """メトリクスカードを更新"""
        if not metric_data:
            return

        # 値を取得
        current = metric_data.get("current")
        avg = metric_data.get("avg")
        max_val = metric_data.get("max")

        # カードの要素を更新
        card.content.content.controls[1].controls[1].value = f"{current:.1f}" if current is not None else "--"
        card.content.content.controls[2].controls[1].value = f"{avg:.1f}" if avg is not None else "--"
        card.content.content.controls[3].controls[1].value = f"{max_val:.1f}" if max_val is not None else "--"
```

## カスタムイベントの追跡

ビジネスロジックに沿ったカスタムイベントの追跡方法を解説します。

### カスタムイベント追跡サービスの実装

```python
# app/services/event_tracker.py
from app.services.analytics import AnalyticsService, EventType
import logging
import time
import json
import os
from enum import Enum
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BusinessEvent(Enum):
    """ビジネスイベント種類"""
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CONTENT_VIEW = "content_view"
    CONTENT_SHARE = "content_share"
    CONTENT_CREATE = "content_create"
    PURCHASE_INITIATED = "purchase_initiated"
    PURCHASE_COMPLETED = "purchase_completed"
    SEARCH_PERFORMED = "search_performed"
    FEATURE_TOGGLE = "feature_toggle"
    APP_RATING = "app_rating"
    TUTORIAL_STEP = "tutorial_step"
    NOTIFICATION_RECEIVED = "notification_received"
    NOTIFICATION_OPENED = "notification_opened"
    ERROR_OCCURRED = "error_occurred"

class EventTracker:
    """カスタムイベント追跡サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(EventTracker, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.analytics = AnalyticsService()
        self.enabled = True

        # イベント履歴の保存先
        self.events_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "events")
        os.makedirs(self.events_dir, exist_ok=True)

        # イベント履歴（最新の100件）
        self.event_history = []
        self.max_history_size = 100

        # セッション情報
        self.session_id = str(int(time.time() * 1000))
        self.session_start_time = time.time()

    def track_event(self, event_type: BusinessEvent, properties: Optional[Dict[str, Any]] = None) -> None:
        """ビジネスイベントを追跡"""
        if not self.enabled:
            return

        if properties is None:
            properties = {}

        # セッション情報を追加
        properties["session_id"] = self.session_id
        properties["session_duration"] = int((time.time() - self.session_start_time) * 1000)

        # イベントをアナリティクスサービスに送信
        self.analytics.log_event(
            EventType.CUSTOM,
            name=event_type.value,
            params=properties
        )

        # イベントを履歴に追加
        event_data = {
            "name": event_type.value,
            "properties": properties,
            "timestamp": int(time.time() * 1000)
        }

        self.event_history.append(event_data)

        # 履歴サイズを制限
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

        # ローカルファイルに保存
        self._save_event(event_data)

        logger.debug(f"イベント追跡: {event_type.value}")

    def _save_event(self, event_data: Dict[str, Any]) -> None:
        """イベントをローカルファイルに保存"""
        try:
            event_id = f"{event_data['timestamp']}_{hash(str(event_data))}"
            event_path = os.path.join(self.events_dir, f"{event_id}.json")

            with open(event_path, 'w') as f:
                json.dump(event_data, f)
        except Exception as e:
            logger.error(f"イベント保存エラー: {e}")

    def get_events(self, event_type: Optional[BusinessEvent] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """イベント履歴を取得"""
        if event_type is None:
            # すべてのイベント
            events = self.event_history[-limit:]
        else:
            # 指定したタイプのイベント
            events = [
                e for e in self.event_history
                if e["name"] == event_type.value
            ][-limit:]

        return events

    def track_user_action(self, action: str, target: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """ユーザーアクション（UIインタラクション）を追跡"""
        if not self.enabled:
            return

        if properties is None:
            properties = {}

        properties["action"] = action
        properties["target"] = target

        self.analytics.log_event(
            EventType.BUTTON_CLICK,
            name=f"{action}_{target}",
            params=properties
        )

        logger.debug(f"ユーザーアクション追跡: {action} on {target}")

    def track_view(self, view_name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """画面表示を追跡"""
        if not self.enabled:
            return

        if properties is None:
            properties = {}

        # 画面表示イベントを追跡
        self.track_event(BusinessEvent.CONTENT_VIEW, {
            "view_name": view_name,
            **properties
        })

    def track_conversion(self, funnel_name: str, step: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """コンバージョンファネルのステップを追跡"""
        if not self.enabled:
            return

        if properties is None:
            properties = {}

        properties["funnel_name"] = funnel_name
        properties["step"] = step

        self.analytics.log_event(
            EventType.CUSTOM,
            name=f"funnel_{funnel_name}_{step}",
            params=properties
        )

        logger.debug(f"コンバージョン追跡: {funnel_name} - {step}")

    def set_enabled(self, enabled: bool) -> None:
        """イベント追跡の有効/無効を切り替え"""
        self.enabled = enabled
        logger.info(f"イベント追跡: {'有効' if enabled else '無効'}")

    def start_new_session(self) -> None:
        """新しいセッションを開始"""
        self.session_id = str(int(time.time() * 1000))
        self.session_start_time = time.time()
        logger.debug(f"新しいセッション開始: {self.session_id}")
```

### イベント追跡の使用例

```python
# app/pages/product_page.py
import flet as ft
from app.services.event_tracker import EventTracker, BusinessEvent

class ProductPage:
    def __init__(self, page: ft.Page, product_id: str):
        self.page = page
        self.product_id = product_id
        self.event_tracker = EventTracker()

        # ページの初期化
        self.init_page()

        # 画面表示イベントを追跡
        self.event_tracker.track_view("product_page", {
            "product_id": product_id,
            "source": page.route
        })

    def init_page(self):
        """ページの初期化"""
        # 商品情報の取得（ダミー）
        product = self.get_product_info(self.product_id)

        # UI要素の作成
        title = ft.Text(product["name"], size=24, weight="bold")

        image = ft.Image(
            src=product["image_url"],
            width=300,
            height=200,
            fit=ft.ImageFit.CONTAIN
        )

        description = ft.Text(product["description"], size=14)

        price = ft.Text(f"¥{product['price']:,}", size=20, weight="bold")

        buy_button = ft.ElevatedButton(
            text="購入する",
            on_click=self.on_buy_button_click
        )

        share_button = ft.OutlinedButton(
            text="シェアする",
            on_click=self.on_share_button_click
        )

        # ページに追加
        self.page.add(
            title,
            image,
            description,
            price,
            ft.Row([buy_button, share_button])
        )

    def get_product_info(self, product_id):
        """商品情報を取得（ダミー）"""
        # 実際のアプリでは、APIやデータベースから取得
        return {
            "id": product_id,
            "name": "サンプル商品",
            "description": "これはサンプル商品の説明です。実際のアプリでは、APIやデータベースから取得したデータを表示します。",
            "price": 9800,
            "image_url": "https://example.com/sample-product.jpg",
            "category": "電子機器"
        }

    def on_buy_button_click(self, e):
        """購入ボタンクリック時の処理"""
        # 購入フローを開始
        self.page.go("/checkout/" + self.product_id)

        # 購入開始イベントを追跡
        self.event_tracker.track_event(BusinessEvent.PURCHASE_INITIATED, {
            "product_id": self.product_id,
            "price": 9800
        })

        # ユーザーアクションを追跡
        self.event_tracker.track_user_action("click", "buy_button", {
            "product_id": self.product_id
        })

        # コンバージョンファネルのステップを追跡
        self.event_tracker.track_conversion("purchase", "initiated", {
            "product_id": self.product_id,
            "from_page": "product_detail"
        })

    def on_share_button_click(self, e):
        """シェアボタンクリック時の処理"""
        # シェアダイアログを表示
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("シェア"),
            content=ft.Text("この商品をシェアします。"),
            actions=[
                ft.TextButton("キャンセル", on_click=self.close_dialog),
                ft.TextButton("シェア", on_click=self.do_share)
            ]
        )
        self.page.dialog.open = True
        self.page.update()

        # ユーザーアクションを追跡
        self.event_tracker.track_user_action("click", "share_button", {
            "product_id": self.product_id
        })

    def close_dialog(self, e):
        """ダイアログを閉じる"""
        self.page.dialog.open = False
        self.page.update()

    def do_share(self, e):
        """実際のシェア処理"""
        # シェアの実装
        self.page.dialog.open = False
        self.page.update()

        # シェアの成功表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("商品をシェアしました！"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

        # シェアイベントを追跡
        self.event_tracker.track_event(BusinessEvent.CONTENT_SHARE, {
            "content_type": "product",
            "content_id": self.product_id,
            "share_method": "dialog"
        })
```

## ユーザーセグメント分析

ユーザーをセグメント化して分析するための実装方法を解説します。

### ユーザープロファイルサービスの実装

```python
# app/services/user_profile.py
import json
import os
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)

class UserProfileService:
    """ユーザープロファイル管理サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(UserProfileService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.analytics = AnalyticsService()

        # ユーザー情報の保存先
        self.profiles_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "profiles")
        os.makedirs(self.profiles_dir, exist_ok=True)

        # 現在のユーザー
        self.current_user_id = None
        self.current_user_profile = None

        # 匿名ユーザーIDの生成または読み込み
        self._init_anonymous_user()

    def _init_anonymous_user(self):
        """匿名ユーザーIDを初期化"""
        user_id_file = os.path.join(self.profiles_dir, "anonymous_user_id.txt")

        if os.path.exists(user_id_file):
            # 既存の匿名ユーザーIDを読み込み
            with open(user_id_file, 'r') as f:
                anonymous_id = f.read().strip()
        else:
            # 新しい匿名ユーザーIDを生成
            anonymous_id = str(uuid.uuid4())
            with open(user_id_file, 'w') as f:
                f.write(anonymous_id)

        # 匿名ユーザープロファイルを読み込み
        self.current_user_id = anonymous_id
        self._load_user_profile(anonymous_id)

        # アナリティクスにユーザーIDをセット
        self.analytics.set_user_id(anonymous_id)

        logger.debug(f"匿名ユーザーID: {anonymous_id}")

    def _load_user_profile(self, user_id):
        """ユーザープロファイルを読み込み"""
        profile_path = os.path.join(self.profiles_dir, f"{user_id}.json")

        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    self.current_user_profile = json.load(f)

                logger.debug(f"ユーザープロファイル読み込み: {user_id}")
            except Exception as e:
                logger.error(f"プロファイル読み込みエラー: {e}")
                self._create_default_profile(user_id)
        else:
            self._create_default_profile(user_id)

    def _create_default_profile(self, user_id):
        """デフォルトのユーザープロファイルを作成"""
        self.current_user_profile = {
            "user_id": user_id,
            "created_at": int(time.time() * 1000),
            "last_active": int(time.time() * 1000),
            "is_anonymous": True,
            "segments": ["new_user"],
            "properties": {},
            "preferences": {},
            "metrics": {
                "app_opens": 1,
                "screen_views": 0,
                "actions": 0,
                "purchases": 0
            }
        }

        self._save_profile()
        logger.debug(f"新規ユーザープロファイル作成: {user_id}")

    def _save_profile(self):
        """ユーザープロファイルを保存"""
        if not self.current_user_id or not self.current_user_profile:
            return

        profile_path = os.path.join(self.profiles_dir, f"{self.current_user_id}.json")

        try:
            with open(profile_path, 'w') as f:
                json.dump(self.current_user_profile, f, indent=2)

            logger.debug(f"ユーザープロファイル保存: {self.current_user_id}")
        except Exception as e:
            logger.error(f"プロファイル保存エラー: {e}")

    def set_identified_user(self, user_id: str, user_data: Optional[Dict[str, Any]] = None) -> None:
        """識別されたユーザーを設定"""
        if user_id == self.current_user_id:
            # すでに同じユーザーが設定されている
            return

        # 新しいユーザーIDを設定
        previous_user_id = self.current_user_id
        self.current_user_id = user_id

        # プロファイルを読み込みまたは作成
        self._load_user_profile(user_id)

        # 匿名ユーザーからの移行の場合
        if previous_user_id and self.current_user_profile.get("is_anonymous", False):
            # 匿名から識別済みに変更
            self.current_user_profile["is_anonymous"] = False
            self.current_user_profile["anonymous_id"] = previous_user_id

        # ユーザーデータがある場合は更新
        if user_data:
            self.update_profile(user_data)

        # アナリティクスにユーザーIDをセット
        self.analytics.set_user_id(user_id)

        # プロファイルを保存
        self._save_profile()

        logger.info(f"識別されたユーザーを設定: {user_id}")

    def update_profile(self, properties: Dict[str, Any]) -> None:
        """ユーザープロファイルを更新"""
        if not self.current_user_profile:
            return

        # プロパティを更新
        if "properties" not in self.current_user_profile:
            self.current_user_profile["properties"] = {}

        self.current_user_profile["properties"].update(properties)

        # 最終アクティブ時間を更新
        self.current_user_profile["last_active"] = int(time.time() * 1000)

        # プロファイルを保存
        self._save_profile()

        # アナリティクスにユーザープロパティをセット
        for key, value in properties.items():
            self.analytics.set_user_property(key, value)

        logger.debug(f"ユーザープロファイル更新: {len(properties)} プロパティ")

    def add_to_segment(self, segment: str) -> None:
        """ユーザーをセグメントに追加"""
        if not self.current_user_profile:
            return

        if "segments" not in self.current_user_profile:
            self.current_user_profile["segments"] = []

        if segment not in self.current_user_profile["segments"]:
            self.current_user_profile["segments"].append(segment)

            # プロファイルを保存
            self._save_profile()

            # アナリティクスにセグメント情報をセット
            self.analytics.set_user_property("segments", ",".join(self.current_user_profile["segments"]))

            logger.debug(f"ユーザーをセグメントに追加: {segment}")

    def remove_from_segment(self, segment: str) -> None:
        """ユーザーをセグメントから削除"""
        if (not self.current_user_profile or
            "segments" not in self.current_user_profile or
            segment not in self.current_user_profile["segments"]):
            return

        self.current_user_profile["segments"].remove(segment)

        # プロファイルを保存
        self._save_profile()

        # アナリティクスにセグメント情報をセット
        self.analytics.set_user_property("segments", ",".join(self.current_user_profile["segments"]))

        logger.debug(f"ユーザーをセグメントから削除: {segment}")

    def get_segments(self) -> List[str]:
        """ユーザーのセグメントを取得"""
        if not self.current_user_profile or "segments" not in self.current_user_profile:
            return []

        return self.current_user_profile["segments"]

    def increment_metric(self, metric: str, value: int = 1) -> None:
        """ユーザーメトリクスをインクリメント"""
        if not self.current_user_profile:
            return

        if "metrics" not in self.current_user_profile:
            self.current_user_profile["metrics"] = {}

        if metric not in self.current_user_profile["metrics"]:
            self.current_user_profile["metrics"][metric] = 0

        self.current_user_profile["metrics"][metric] += value

        # プロファイルを保存
        self._save_profile()

        logger.debug(f"ユーザーメトリクス更新: {metric}={self.current_user_profile['metrics'][metric]}")

    def set_preference(self, key: str, value: Any) -> None:
        """ユーザー設定を保存"""
        if not self.current_user_profile:
            return

        if "preferences" not in self.current_user_profile:
            self.current_user_profile["preferences"] = {}

        self.current_user_profile["preferences"][key] = value

        # プロファイルを保存
        self._save_profile()

        logger.debug(f"ユーザー設定保存: {key}={value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """ユーザー設定を取得"""
        if (not self.current_user_profile or
            "preferences" not in self.current_user_profile or
            key not in self.current_user_profile["preferences"]):
            return default

        return self.current_user_profile["preferences"][key]

    def get_current_user_id(self) -> Optional[str]:
        """現在のユーザーIDを取得"""
        return self.current_user_id

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """現在のユーザープロファイルを取得"""
        return self.current_user_profile

    def on_app_open(self) -> None:
        """アプリ起動時の処理"""
        if not self.current_user_profile:
            return

        # 最終アクティブ時間を更新
        self.current_user_profile["last_active"] = int(time.time() * 1000)

        # アプリ起動回数をインクリメント
        self.increment_metric("app_opens")

        # 初回起動からの経過日数を計算
        if "created_at" in self.current_user_profile:
            days_since_install = (int(time.time() * 1000) - self.current_user_profile["created_at"]) // (24 * 60 * 60 * 1000)

            # 30日以上経過していれば「既存ユーザー」セグメントに追加
            if days_since_install >= 30 and "new_user" in self.get_segments():
                self.remove_from_segment("new_user")
                self.add_to_segment("existing_user")

            # プロパティとして経過日数を設定
            self.update_profile({"days_since_install": days_since_install})
```

### ユーザーセグメント分析の使用例

```python
# app/main.py
import flet as ft
from app.services.user_profile import UserProfileService
from app.services.event_tracker import EventTracker, BusinessEvent

def main(page: ft.Page):
    # ユーザープロファイルサービスの初期化
    user_profile = UserProfileService()
    event_tracker = EventTracker()

    # アプリ起動処理
    user_profile.on_app_open()

    # アプリ起動イベントの追跡
    event_tracker.track_event(BusinessEvent.APP_OPEN)

    # ページ初期化
    page.title = "Fletアプリ"

    # セグメントに基づいた表示内容のカスタマイズ
    def show_personalized_content():
        segments = user_profile.get_segments()

        # 新規ユーザー向けコンテンツ
        if "new_user" in segments:
            page.add(
                ft.Text("初めてのご利用ありがとうございます！", size=20, weight="bold"),
                ft.ElevatedButton("チュートリアルを見る", on_click=show_tutorial)
            )

        # 既存ユーザー向けコンテンツ
        elif "existing_user" in segments:
            last_viewed = user_profile.get_preference("last_viewed_category", "general")
            page.add(
                ft.Text(f"おかえりなさい！", size=20, weight="bold"),
                ft.Text(f"前回は「{last_viewed}」カテゴリを見ていました")
            )

        # 高頻度ユーザー向けコンテンツ
        if "power_user" in segments:
            page.add(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text("パワーユーザー特典", weight="bold"),
                            ft.Text("新機能のベータテストに参加しませんか？")
                        ])
                    )
                )
            )

        # 全ユーザー向けコンテンツ
        page.add(
            ft.Text("コンテンツセクション", size=16, weight="bold"),
            ft.ListView([
                create_content_item("記事1", "category1"),
                create_content_item("記事2", "category2"),
                create_content_item("記事3", "category3")
            ])
        )

    def create_content_item(title, category):
        return ft.ListTile(
            title=ft.Text(title),
            subtitle=ft.Text(category),
            trailing=ft.Icon(ft.icons.ARROW_FORWARD),
            on_click=lambda e: on_content_click(title, category)
        )

    def on_content_click(title, category):
        # コンテンツ閲覧イベントを追跡
        event_tracker.track_event(BusinessEvent.CONTENT_VIEW, {
            "content_title": title,
            "content_category": category
        })

        # ユーザー設定を更新
        user_profile.set_preference("last_viewed_category", category)

        # 閲覧回数をインクリメント
        user_profile.increment_metric("content_views")

        # 閲覧回数によるセグメント分析
        metrics = user_profile.get_profile().get("metrics", {})
        if metrics.get("content_views", 0) > 10:
            user_profile.add_to_segment("engaged_reader")

        if metrics.get("content_views", 0) > 50:
            user_profile.add_to_segment("power_user")

        # ページ遷移
        page.go(f"/content/{category}/{title}")

    def show_tutorial(e):
        # チュートリアル表示処理
        # ...

        # イベント追跡
        event_tracker.track_event(BusinessEvent.TUTORIAL_STEP, {
            "step": 1,
            "action": "start"
        })

    # ログインボタン（匿名ユーザーの場合）
    if user_profile.get_profile().get("is_anonymous", True):
        def on_login(e):
            # デモ用：実際のアプリではサーバーと認証する
            user_id = "user123"
            user_data = {
                "name": "サンプルユーザー",
                "email": "sample@example.com",
                "registration_date": int(time.time() * 1000)
            }

            # 識別されたユーザーをセット
            user_profile.set_identified_user(user_id, user_data)

            # ログインイベントを追跡
            event_tracker.track_event(BusinessEvent.USER_LOGIN, {
                "login_method": "email"
            })

            # ページを更新
            page.clean()
            show_personalized_content()
            page.update()

        page.add(
            ft.ElevatedButton("ログイン", on_click=on_login)
        )

    # パーソナライズドコンテンツの表示
    show_personalized_content()

if __name__ == "__main__":
    ft.app(target=main)
```

## A/Bテストの実装

機能やUIの効果を測定するためのA/Bテストの実装方法を解説します。

### A/Bテストサービスの実装

```python
# app/services/ab_test.py
import json
import os
import random
import hashlib
import logging
from typing import Dict, Any, List, Optional
from app.services.user_profile import UserProfileService
from app.services.event_tracker import EventTracker, BusinessEvent

logger = logging.getLogger(__name__)

class ABTest:
    """A/Bテスト実験定義"""

    def __init__(self, test_id, variants, traffic_allocation=1.0, description=None):
        """
        Args:
            test_id (str): テストID
            variants (list): バリアント定義のリスト
            traffic_allocation (float): 0.0～1.0の値。ユーザーのうち何割をテストに参加させるか
            description (str, optional): テストの説明
        """
        self.test_id = test_id
        self.variants = variants
        self.traffic_allocation = traffic_allocation
        self.description = description or ""

class ABTestService:
    """A/Bテストサービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(ABTestService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.user_profile = UserProfileService()
        self.event_tracker = EventTracker()

        # 実験設定ファイルのパス
        self.config_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "abtest")
        os.makedirs(self.config_dir, exist_ok=True)

        # アクティブな実験リスト
        self.active_tests = {}

        # 設定を読み込み
        self._load_tests()

    def _load_tests(self):
        """テスト設定を読み込み"""
        config_path = os.path.join(self.config_dir, "experiments.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    tests_config = json.load(f)

                for test_config in tests_config:
                    test = ABTest(
                        test_id=test_config["test_id"],
                        variants=test_config["variants"],
                        traffic_allocation=test_config.get("traffic_allocation", 1.0),
                        description=test_config.get("description", "")
                    )
                    self.active_tests[test.test_id] = test

                logger.info(f"{len(self.active_tests)}件のA/Bテスト設定を読み込み")
            except Exception as e:
                logger.error(f"テスト設定読み込みエラー: {e}")
        else:
            # サンプルテスト設定を作成
            self._create_sample_tests()

    def _create_sample_tests(self):
        """サンプルテスト設定を作成"""
        sample_tests = [
            {
                "test_id": "homepage_layout",
                "variants": [
                    {"id": "control", "name": "従来のレイアウト", "weight": 0.5},
                    {"id": "variant_a", "name": "新レイアウト", "weight": 0.5}
                ],
                "traffic_allocation": 1.0,
                "description": "ホームページレイアウトのテスト"
            },
            {
                "test_id": "cta_button_color",
                "variants": [
                    {"id": "blue", "name": "青色ボタン", "weight": 0.33},
                    {"id": "green", "name": "緑色ボタン", "weight": 0.33},
                    {"id": "red", "name": "赤色ボタン", "weight": 0.34}
                ],
                "traffic_allocation": 0.8,
                "description": "CTA（行動喚起）ボタンの色テスト"
            }
        ]

        # 設定ファイルに保存
        config_path = os.path.join(self.config_dir, "experiments.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(sample_tests, f, indent=2)

            # テストをロード
            for test_config in sample_tests:
                test = ABTest(
                    test_id=test_config["test_id"],
                    variants=test_config["variants"],
                    traffic_allocation=test_config.get("traffic_allocation", 1.0),
                    description=test_config.get("description", "")
                )
                self.active_tests[test.test_id] = test

            logger.info(f"{len(sample_tests)}件のサンプルA/Bテスト設定を作成")
        except Exception as e:
            logger.error(f"サンプルテスト設定作成エラー: {e}")

    def get_variant(self, test_id: str) -> Optional[Dict[str, Any]]:
        """ユーザーのテストバリアントを取得"""
        if test_id not in self.active_tests:
            logger.warning(f"テストID {test_id} は存在しません")
            return None

        # 現在のユーザーID
        user_id = self.user_profile.get_current_user_id()
        if not user_id:
            logger.warning("ユーザーIDが取得できません")
            return None

        # ユーザープロファイルからバリアント割り当てを確認
        profile = self.user_profile.get_profile()
        if profile and "ab_tests" in profile and test_id in profile["ab_tests"]:
            # 既に割り当てられたバリアント
            variant_id = profile["ab_tests"][test_id]

            # バリアント情報を検索
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant["id"] == variant_id:
                    return variant

        # 新規割り当て
        variant = self._assign_variant(test_id, user_id)
        if variant:
            self._save_variant_assignment(test_id, variant["id"])

        return variant

    def _assign_variant(self, test_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """バリアントを割り当て"""
        test = self.active_tests[test_id]

        # トラフィック割り当て（一部のユーザーのみテストに参加）
        if test.traffic_allocation < 1.0:
            # ユーザーIDからハッシュ値を生成し、0.0～1.0の値に正規化
            hash_val = int(hashlib.md5(f"{test_id}:{user_id}".encode()).hexdigest(), 16)
            normalized_hash = hash_val / (2**128 - 1)  # 0.0～1.0の値に正規化

            if normalized_hash > test.traffic_allocation:
                logger.debug(f"ユーザー {user_id} はテスト {test_id} に参加しません")
                return None

        # バリアントの重みを正規化
        total_weight = sum(variant["weight"] for variant in test.variants)
        normalized_weights = [variant["weight"] / total_weight for variant in test.variants]

        # バリアントを選択（ランダムではなく、ユーザーIDに基づいて決定的に選択）
        hash_val = int(hashlib.md5(f"{test_id}:{user_id}".encode()).hexdigest(), 16)
        normalized_hash = hash_val / (2**128 - 1)  # 0.0～1.0の値に正規化

        cumulative_prob = 0
        for i, weight in enumerate(normalized_weights):
            cumulative_prob += weight
            if normalized_hash < cumulative_prob:
                logger.debug(f"ユーザー {user_id} にテスト {test_id} のバリアント {test.variants[i]['id']} を割り当て")

                # バリアントの露出をトラッキング
                self.event_tracker.track_event(BusinessEvent.CUSTOM, {
                    "event_type": "experiment_exposure",
                    "test_id": test_id,
                    "variant_id": test.variants[i]["id"]
                })

                return test.variants[i]

        # デフォルトケース（通常は到達しない）
        return test.variants[0] if test.variants else None

    def _save_variant_assignment(self, test_id: str, variant_id: str) -> None:
        """バリアント割り当てを保存"""
        profile = self.user_profile.get_profile()
        if not profile:
            return

        # A/Bテスト割り当てを保存
        if "ab_tests" not in profile:
            profile["ab_tests"] = {}

        profile["ab_tests"][test_id] = variant_id

        # プロファイルを更新
        self.user_profile._save_profile()

    def track_conversion(self, test_id: str, event: str, properties: Optional[Dict[str, Any]] = None) -> None:
        """テストのコンバージョンイベントを追跡"""
        # バリアントを取得
        variant = self.get_variant(test_id)
        if not variant:
            return

        # プロパティが未指定の場合は空辞書を使用
        event_properties = properties or {}

        # テスト情報を追加
        event_properties.update({
            "test_id": test_id,
            "variant_id": variant["id"],
            "variant_name": variant.get("name", variant["id"]),
            "conversion_event": event
        })

        # イベントを追跡
        self.event_tracker.track_event(BusinessEvent.CUSTOM, event_properties)

        logger.debug(f"コンバージョン追跡: {test_id} - {event} - {variant['id']}")

    def get_active_tests(self) -> List[Dict[str, Any]]:
        """アクティブなテスト一覧を取得"""
        return [
            {
                "test_id": test.test_id,
                "description": test.description,
                "variants": test.variants,
                "traffic_allocation": test.traffic_allocation
            }
            for test in self.active_tests.values()
        ]
```

### A/Bテストの使用例

```python
# app/pages/home_page.py
import flet as ft
from app.services.ab_test import ABTestService
from app.services.user_profile import UserProfileService
from app.services.event_tracker import EventTracker, BusinessEvent

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ab_test = ABTestService()
        self.user_profile = UserProfileService()
        self.event_tracker = EventTracker()

        # ページの初期化
        self.init_page()

        # 画面表示イベントを追跡
        self.event_tracker.track_view("home_page")

    def init_page(self):
        """ページの初期化"""
        self.page.title = "ホーム"

        # ホームページレイアウトのA/Bテスト
        layout_variant = self.ab_test.get_variant("homepage_layout")

        if layout_variant and layout_variant["id"] == "variant_a":
            # 新レイアウト
            self.init_new_layout()
        else:
            # 従来のレイアウト（デフォルト）
            self.init_default_layout()

    def init_default_layout(self):
        """従来のレイアウト"""
        # ヘッダー
        header = ft.AppBar(
            title=ft.Text("Fletアプリ"),
            center_title=False,
            bgcolor=ft.colors.BLUE
        )

        # メインコンテンツ
        content = ft.Column([
            ft.Text("おすすめコンテンツ", size=20, weight="bold"),
            ft.ListView([
                self.create_content_item("アイテム1"),
                self.create_content_item("アイテム2"),
                self.create_content_item("アイテム3")
            ]),
            self.create_cta_button()
        ])

        self.page.appbar = header
        self.page.add(content)

    def init_new_layout(self):
        """新レイアウト"""
        # ヘッダー（新デザイン）
        header = ft.AppBar(
            title=ft.Text("Fletアプリ"),
            center_title=True,
            bgcolor=ft.colors.INDIGO_700
        )

        # ヒーローセクション
        hero = ft.Container(
            height=200,
            padding=ft.padding.all(20),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.colors.BLUE_700, ft.colors.INDIGO_900]
            ),
            content=ft.Column([
                ft.Text("より良いアプリ体験", size=28, weight="bold", color=ft.colors.WHITE),
                ft.Text("新しいデザインでより使いやすく", size=16, color=ft.colors.WHITE)
            ])
        )

        # メインコンテンツ（カード形式）
        content_items = ft.Row([
            self.create_content_card("アイテム1"),
            self.create_content_card("アイテム2"),
            self.create_content_card("アイテム3")
        ], scroll="auto")

        # フッター
        footer = ft.Container(
            padding=ft.padding.all(20),
            content=self.create_cta_button()
        )

        self.page.appbar = header
        self.page.add(hero, content_items, footer)

    def create_content_item(self, title):
        """コンテンツアイテムを作成（従来のレイアウト用）"""
        return ft.ListTile(
            title=ft.Text(title),
            trailing=ft.Icon(ft.icons.ARROW_FORWARD),
            on_click=lambda e: self.on_content_click(title)
        )

    def create_content_card(self, title):
        """コンテンツカードを作成（新レイアウト用）"""
        return ft.Card(
            width=150,
            height=180,
            content=ft.Container(
                padding=ft.padding.all(10),
                content=ft.Column([
                    ft.Icon(ft.icons.ARTICLE, size=50),
                    ft.Text(title, size=16, weight="bold"),
                    ft.Text("コンテンツの説明", size=12)
                ], alignment=ft.MainAxisAlignment.CENTER),
                on_click=lambda e: self.on_content_click(title)
            )
        )

    def create_cta_button(self):
        """CTA（行動喚起）ボタンを作成"""
        # ボタンの色のA/Bテスト
        button_variant = self.ab_test.get_variant("cta_button_color")

        button_color = ft.colors.BLUE
        if button_variant:
            if button_variant["id"] == "green":
                button_color = ft.colors.GREEN
            elif button_variant["id"] == "red":
                button_color = ft.colors.RED

        return ft.ElevatedButton(
            text="今すぐ始める",
            style=ft.ButtonStyle(
                bgcolor=button_color,
                color=ft.colors.WHITE,
                padding=ft.padding.all(20)
            ),
            on_click=self.on_cta_click
        )

    def on_content_click(self, title):
        """コンテンツクリック時の処理"""
        # コンテンツ閲覧をトラッキング
        self.event_tracker.track_event(BusinessEvent.CONTENT_VIEW, {
            "content_title": title
        })

        # レイアウトテストのコンバージョンを追跡
        self.ab_test.track_conversion("homepage_layout", "content_click", {
            "content_title": title
        })

        # ページ遷移
        self.page.go(f"/content/{title}")

    def on_cta_click(self, e):
        """CTAボタンクリック時の処理"""
        # CTAクリックをトラッキング
        self.event_tracker.track_event(BusinessEvent.BUTTON_CLICK, {
            "button": "cta",
            "location": "home_page"
        })

        # ボタン色テストのコンバージョンを追跡
        self.ab_test.track_conversion("cta_button_color", "button_click")

        # ページ遷移
        self.page.go("/signup")
```

### A/Bテスト結果のダッシュボード

```python
# app/pages/ab_test_dashboard.py
import flet as ft
from app.services.ab_test import ABTestService

class ABTestDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.ab_test = ABTestService()

        # ダッシュボードの初期化
        self.init_dashboard()

    def init_dashboard(self):
        """ダッシュボードの初期化"""
        self.page.title = "A/Bテスト結果"

        # ヘッダー
        header = ft.AppBar(
            title=ft.Text("A/Bテスト分析"),
            bgcolor=ft.colors.BLUE
        )

        # テスト一覧
        active_tests = self.ab_test.get_active_tests()

        test_sections = []
        for test in active_tests:
            test_sections.append(self.create_test_section(test))

        # レイアウト
        self.page.appbar = header
        self.page.add(
            ft.Text("アクティブなテスト一覧", size=24, weight="bold"),
            ft.Column(test_sections)
        )

    def create_test_section(self, test):
        """テストセクションを作成"""
        variants_text = ", ".join([f"{v['name']} ({v['weight'] * 100:.0f}%)" for v in test["variants"]])

        return ft.Container(
            padding=ft.padding.all(10),
            margin=ft.margin.only(bottom=20),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            content=ft.Column([
                ft.Text(test["test_id"], size=20, weight="bold"),
                ft.Text(test["description"]),
                ft.Text(f"トラフィック配分: {test['traffic_allocation'] * 100:.0f}%", size=14),
                ft.Text(f"バリアント: {variants_text}", size=14),

                # 結果グラフは、実際にはAPIからデータを取得して表示
                ft.Container(
                    padding=ft.padding.all(10),
                    bgcolor=ft.colors.GREY_200,
                    border_radius=5,
                    content=ft.Column([
                        ft.Text("※ このデモでは実際の結果データは表示されません", italic=True),
                        ft.Text("※ 実際のアプリでは、分析APIからデータを取得して表示します", italic=True)
                    ])
                )
            ])
        )
```

## リモート構成（Remote Config）

アプリの動作をサーバーから制御するためのリモート構成（Remote Config）機能の実装方法を解説します。

### リモート構成サービスの実装

```python
# app/services/remote_config.py
import json
import os
import time
import logging
import random
import hashlib
import requests
from typing import Dict, Any, Optional
from app.services.user_profile import UserProfileService

logger = logging.getLogger(__name__)

class RemoteConfigService:
    """リモート構成サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(RemoteConfigService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.user_profile = UserProfileService()

        # 設定ファイルのパス
        self.config_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "config")
        os.makedirs(self.config_dir, exist_ok=True)

        # デフォルト設定
        self.default_config = {}

        # 取得済み設定
        self.fetched_config = {}

        # 最終更新時間
        self.last_fetch_time = 0

        # 有効化された設定
        self.active_config = {}

        # デフォルト設定の読み込み
        self._load_default_config()

        # キャッシュからの読み込み
        self._load_cached_config()

    def _load_default_config(self):
        """デフォルト設定を読み込み"""
        default_path = os.path.join(self.config_dir, "default_config.json")

        if os.path.exists(default_path):
            try:
                with open(default_path, 'r') as f:
                    self.default_config = json.load(f)

                logger.debug(f"デフォルト設定を読み込み: {len(self.default_config)}項目")
            except Exception as e:
                logger.error(f"デフォルト設定読み込みエラー: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """デフォルト設定を作成"""
        self.default_config = {
            "app_theme": "light",
            "welcome_message": "ようこそ、Fletアプリへ！",
            "feature_flags": {
                "new_ui_enabled": False,
                "premium_features": False,
                "debug_mode": False
            },
            "app_config": {
                "cache_ttl_seconds": 3600,
                "api_timeout_ms": 5000,
                "max_retry_count": 3
            },
            "ui_config": {
                "primary_color": "#2196F3",
                "font_size": "medium",
                "animation_speed": "normal"
            }
        }

        # 設定ファイルに保存
        default_path = os.path.join(self.config_dir, "default_config.json")
        try:
            with open(default_path, 'w') as f:
                json.dump(self.default_config, f, indent=2)

            logger.info("デフォルト設定を作成")
        except Exception as e:
            logger.error(f"デフォルト設定作成エラー: {e}")

        # アクティブ設定としてデフォルト値を使用
        self.active_config = self.default_config.copy()

    def _load_cached_config(self):
        """キャッシュから設定を読み込み"""
        cache_path = os.path.join(self.config_dir, "cached_config.json")

        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)

                self.fetched_config = cache_data.get("config", {})
                self.last_fetch_time = cache_data.get("fetch_time", 0)

                # 設定を有効化
                self._activate_config()

                logger.debug(f"キャッシュから設定を読み込み: {len(self.fetched_config)}項目")
            except Exception as e:
                logger.error(f"キャッシュ読み込みエラー: {e}")

    def _save_cached_config(self):
        """設定をキャッシュに保存"""
        cache_path = os.path.join(self.config_dir, "cached_config.json")

        try:
            cache_data = {
                "config": self.fetched_config,
                "fetch_time": self.last_fetch_time
            }

            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug("設定をキャッシュに保存")
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")

    def fetch_config(self, force_refresh=False):
        """サーバーから設定を取得"""
        # 最後の取得から1時間以内の場合はスキップ（強制更新オプションなし）
        current_time = time.time()
        if not force_refresh and (current_time - self.last_fetch_time) < 3600:
            logger.debug("キャッシュが有効なため、取得をスキップ")
            return False

        try:
            # サーバーから設定を取得（実際の実装ではAPI呼び出し）
            # 例: response = requests.get("https://api.example.com/remote_config")

            # デモ用：サーバーAPIのシミュレーション
            # 実際のアプリでは、Firebase Remote ConfigやカスタムAPIを使用
            user_id = self.user_profile.get_current_user_id()

            # デモ設定を生成
            demo_config = {
                "app_theme": random.choice(["light", "dark", "auto"]),
                "welcome_message": "リモート設定からのメッセージです！",
                "feature_flags": {
                    "new_ui_enabled": random.random() > 0.5,
                    "premium_features": False,
                    "debug_mode": False
                },
                "app_config": {
                    "cache_ttl_seconds": 7200,
                    "api_timeout_ms": 10000,
                    "max_retry_count": 5
                },
                "ui_config": {
                    "primary_color": random.choice(["#2196F3", "#4CAF50", "#F44336"]),
                    "font_size": random.choice(["small", "medium", "large"]),
                    "animation_speed": random.choice(["slow", "normal", "fast"])
                }
            }

            # ユーザーセグメントに基づいた設定の適用
            user_segments = self.user_profile.get_segments()
            if "power_user" in user_segments:
                demo_config["feature_flags"]["premium_features"] = True

            if "developer" in user_segments:
                demo_config["feature_flags"]["debug_mode"] = True

            # 取得した設定を保存
            self.fetched_config = demo_config
            self.last_fetch_time = current_time

            # 設定をキャッシュに保存
            self._save_cached_config()

            # 設定を有効化
            self._activate_config()

            logger.info("リモート設定を更新")
            return True

        except Exception as e:
            logger.error(f"リモート設定取得エラー: {e}")
            return False

    def _activate_config(self):
        """設定を有効化（デフォルト設定とリモート設定をマージ）"""
        # デフォルト設定をベースにする
        self.active_config = self.default_config.copy()

        # 取得した設定を上書き
        self._deep_merge(self.active_config, self.fetched_config)

        logger.debug("設定を有効化")

    def _deep_merge(self, target, source):
        """ディクショナリを再帰的にマージ"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # 再帰的にマージ
                self._deep_merge(target[key], value)
            else:
                # 値を上書き
                target[key] = value

    def get_value(self, key, default=None):
        """設定値を取得"""
        # キーのパスを分割（例: "feature_flags.new_ui_enabled"）
        parts = key.split('.')

        # アクティブ設定から値を検索
        value = self.active_config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_all(self):
        """すべての設定を取得"""
        return self.active_config.copy()

    def is_feature_enabled(self, feature_name):
        """機能フラグが有効かどうかを確認"""
        return self.get_value(f"feature_flags.{feature_name}", False)
```

### リモート構成の使用例

```python
# app/pages/settings_page.py
import flet as ft
from app.services.remote_config import RemoteConfigService
from app.services.user_profile import UserProfileService

class SettingsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.remote_config = RemoteConfigService()
        self.user_profile = UserProfileService()

        # リモート設定を取得（必要に応じて）
        self.remote_config.fetch_config()

        # ページの初期化
        self.init_page()

    def init_page(self):
        """ページの初期化"""
        # ページタイトル
        self.page.title = "設定"

        # テーマの取得
        theme = self.remote_config.get_value("app_theme", "light")

        # テーマドロップダウン
        theme_dropdown = ft.Dropdown(
            label="テーマ",
            width=200,
            options=[
                ft.dropdown.Option("light", "ライト"),
                ft.dropdown.Option("dark", "ダーク"),
                ft.dropdown.Option("auto", "自動（システム設定に従う）")
            ],
            value=theme,
            on_change=self.on_theme_change
        )

        # フォントサイズの取得
        font_size = self.remote_config.get_value("ui_config.font_size", "medium")

        # フォントサイズラジオボタン
        font_size_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Text("フォントサイズ:"),
                ft.Row([
                    ft.Radio(value="small", label="小"),
                    ft.Radio(value="medium", label="中"),
                    ft.Radio(value="large", label="大")
                ])
            ]),
            value=font_size,
            on_change=self.on_font_size_change
        )

        # アニメーション速度の取得
        animation_speed = self.remote_config.get_value("ui_config.animation_speed", "normal")

        # アニメーション速度スライダー
        animation_speed_slider = ft.Column([
            ft.Text("アニメーション速度:"),
            ft.Slider(
                min=0,
                max=2,
                divisions=2,
                value={"slow": 0, "normal": 1, "fast": 2}[animation_speed],
                labels={"0": "遅い", "1": "普通", "2": "速い"},
                on_change=self.on_animation_speed_change
            )
        ])

        # 更新ボタン
        refresh_button = ft.ElevatedButton(
            "設定を更新",
            on_click=self.on_refresh_click
        )

        # プレミアム機能セクション
        premium_section = None
        if self.remote_config.is_feature_enabled("premium_features"):
            premium_section = ft.Container(
                padding=ft.padding.all(10),
                bgcolor=ft.colors.AMBER_100,
                border_radius=5,
                content=ft.Column([
                    ft.Text("プレミアム機能", size=16, weight="bold"),
                    ft.Text("あなたはプレミアム機能にアクセスできます！")
                ])
            )

        # デバッグモードセクション
        debug_section = None
        if self.remote_config.is_feature_enabled("debug_mode"):
            all_config = self.remote_config.get_all()
            config_text = json.dumps(all_config, indent=2)

            debug_section = ft.Container(
                padding=ft.padding.all(10),
                bgcolor=ft.colors.GREY_200,
                border_radius=5,
                content=ft.Column([
                    ft.Text("デバッグモード", size=16, weight="bold"),
                    ft.Text("現在の設定:"),
                    ft.TextField(
                        value=config_text,
                        multiline=True,
                        read_only=True,
                        min_lines=10,
                        max_lines=20
                    )
                ])
            )

        # レイアウト
        settings_column = ft.Column([
            ft.Text("アプリ設定", size=24, weight="bold"),
            theme_dropdown,
            font_size_radio,
            animation_speed_slider,
            refresh_button
        ])

        if premium_section:
            settings_column.controls.append(ft.Divider())
            settings_column.controls.append(premium_section)

        if debug_section:
            settings_column.controls.append(ft.Divider())
            settings_column.controls.append(debug_section)

        # ページに追加
        self.page.add(settings_column)

    def on_theme_change(self, e):
        """テーマ変更時の処理"""
        # ユーザー設定を保存
        self.user_profile.set_preference("app_theme", e.control.value)

        # 実際のテーマを変更（アプリのメイン処理で適用）
        pass

    def on_font_size_change(self, e):
        """フォントサイズ変更時の処理"""
        # ユーザー設定を保存
        self.user_profile.set_preference("font_size", e.control.value)

        # 実際のフォントサイズを変更（アプリのメイン処理で適用）
        pass

    def on_animation_speed_change(self, e):
        """アニメーション速度変更時の処理"""
        speed_value = e.control.value
        speed_name = ["slow", "normal", "fast"][int(speed_value)]

        # ユーザー設定を保存
        self.user_profile.set_preference("animation_speed", speed_name)

        # 実際のアニメーション速度を変更（アプリのメイン処理で適用）
        pass

    def on_refresh_click(self, e):
        """更新ボタンクリック時の処理"""
        # プログレスインジケータの表示
        progress = ft.ProgressBar(width=400)
        self.page.add(progress)
        self.page.update()

        # リモート設定を強制更新
        success = self.remote_config.fetch_config(force_refresh=True)

        # プログレスインジケータを削除
        self.page.controls.remove(progress)

        # 結果を表示
        if success:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("設定を更新しました"),
                action="閉じる"
            )
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("設定の更新に失敗しました"),
                action="閉じる"
            )

        self.page.snack_bar.open = True

        # ページを再描画
        self.page.clean()
        self.init_page()
        self.page.update()
```

## プライバシーとコンプライアンス

アプリ分析におけるプライバシーとコンプライアンスの考慮事項について解説します。

### プライバシー設定サービスの実装

```python
# app/services/privacy_service.py
import json
import os
import logging
from typing import Dict, Any, List, Set, Optional
from app.services.user_profile import UserProfileService

logger = logging.getLogger(__name__)

class PrivacyService:
    """プライバシー設定サービス"""

    _instance = None

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(PrivacyService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """サービスの初期化"""
        self.user_profile = UserProfileService()

        # プライバシー設定ファイルのパス
        self.config_dir = os.path.join(os.path.expanduser("~"), ".flet-app", "privacy")
        os.makedirs(self.config_dir, exist_ok=True)

        # プライバシー設定
        self.privacy_settings = {}

        # プライバシー設定の読み込み
        self._load_privacy_settings()

    def _load_privacy_settings(self):
        """プライバシー設定を読み込み"""
        settings_path = os.path.join(self.config_dir, "privacy_settings.json")

        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    self.privacy_settings = json.load(f)

                logger.debug("プライバシー設定を読み込み")
            except Exception as e:
                logger.error(f"プライバシー設定読み込みエラー: {e}")
                self._create_default_settings()
        else:
            self._create_default_settings()

    def _create_default_settings(self):
        """デフォルトのプライバシー設定を作成"""
        # ユーザープロファイルからユーザーIDを取得
        user_id = self.user_profile.get_current_user_id()

        self.privacy_settings = {
            "user_id": user_id,
            "consents": {
                "analytics": True,
                "crash_reports": True,
                "personalization": True,
                "marketing": False
            },
            "data_retention": {
                "analytics_days": 90,
                "personal_data_days": 365
            },
            "data_subjects_rights": {
                "access_requested": False,
                "deletion_requested": False,
                "last_request_timestamp": None
            },
            "anonymize_data": False
        }

        # 設定ファイルに保存
        self._save_privacy_settings()

        logger.info("デフォルトのプライバシー設定を作成")

    def _save_privacy_settings(self):
        """プライバシー設定を保存"""
        settings_path = os.path.join(self.config_dir, "privacy_settings.json")

        try:
            with open(settings_path, 'w') as f:
                json.dump(self.privacy_settings, f, indent=2)

            logger.debug("プライバシー設定を保存")
        except Exception as e:
            logger.error(f"プライバシー設定保存エラー: {e}")

    def has_consent(self, consent_type):
        """指定した種類の同意があるかを確認"""
        if "consents" not in self.privacy_settings:
            return False

        return self.privacy_settings["consents"].get(consent_type, False)

    def update_consent(self, consent_type, value):
        """同意設定を更新"""
        if "consents" not in self.privacy_settings:
            self.privacy_settings["consents"] = {}

        self.privacy_settings["consents"][consent_type] = value

        # 設定を保存
        self._save_privacy_settings()

        logger.info(f"同意設定を更新: {consent_type}={value}")

        # 各サービスの有効/無効を切り替え
        self._update_services_state()

        return True

    def update_multiple_consents(self, consent_dict):
        """複数の同意設定を一括更新"""
        if "consents" not in self.privacy_settings:
            self.privacy_settings["consents"] = {}

        for consent_type, value in consent_dict.items():
            self.privacy_settings["consents"][consent_type] = value

        # 設定を保存
        self._save_privacy_settings()

        logger.info(f"複数の同意設定を更新: {len(consent_dict)}件")

        # 各サービスの有効/無効を切り替え
        self._update_services_state()

        return True

    def _update_services_state(self):
        """各サービスの有効/無効を同意設定に基づいて切り替え"""
        try:
            # 同意設定の取得
            analytics_enabled = self.has_consent("analytics")
            crash_reports_enabled = self.has_consent("crash_reports")
            personalization_enabled = self.has_consent("personalization")

            # アナリティクスサービスの有効/無効を切り替え
            from app.services.analytics import AnalyticsService
            analytics = AnalyticsService()
            analytics.set_enabled(analytics_enabled)

            # クラッシュレポートサービスの有効/無効を切り替え
            from app.services.crash_reporter import CrashReporter
            crash_reporter = CrashReporter()
            crash_reporter.set_enabled(crash_reports_enabled)

            # イベント追跡サービスの有効/無効を切り替え
            from app.services.event_tracker import EventTracker
            event_tracker = EventTracker()
            event_tracker.set_enabled(analytics_enabled)

            # パフォーマンスモニタリングサービスの有効/無効を切り替え
            from app.services.performance import PerformanceMonitor
            performance_monitor = PerformanceMonitor()
            performance_monitor.set_enabled(analytics_enabled)

            logger.debug("サービスの状態を更新")
        except Exception as e:
            logger.error(f"サービス状態更新エラー: {e}")

    def request_data_access(self):
        """データアクセス要求を記録"""
        if "data_subjects_rights" not in self.privacy_settings:
            self.privacy_settings["data_subjects_rights"] = {}

        import time
        self.privacy_settings["data_subjects_rights"]["access_requested"] = True
        self.privacy_settings["data_subjects_rights"]["last_request_timestamp"] = int(time.time())

        # 設定を保存
        self._save_privacy_settings()

        logger.info("データアクセス要求を記録")

        # 実際のアプリでは、ここでデータアクセス要求を処理するバックエンドAPIを呼び出す

        return True

    def request_data_deletion(self):
        """データ削除要求を記録"""
        if "data_subjects_rights" not in self.privacy_settings:
            self.privacy_settings["data_subjects_rights"] = {}

        import time
        self.privacy_settings["data_subjects_rights"]["deletion_requested"] = True
        self.privacy_settings["data_subjects_rights"]["last_request_timestamp"] = int(time.time())

        # 設定を保存
        self._save_privacy_settings()

        logger.info("データ削除要求を記録")

        # 実際のアプリでは、ここでデータ削除要求を処理するバックエンドAPIを呼び出す

        return True

    def set_anonymize_data(self, value):
        """データ匿名化設定を更新"""
        self.privacy_settings["anonymize_data"] = value

        # 設定を保存
        self._save_privacy_settings()

        logger.info(f"データ匿名化設定を更新: {value}")

        # ユーザーIDの匿名化処理
        if value:
            self._anonymize_user_data()

        return True

    def _anonymize_user_data(self):
        """ユーザーデータを匿名化"""
        # 実際のアプリでは、ここでユーザーデータの匿名化処理を行う
        # - 個人を特定できる情報を削除
        # - IPアドレスを切り詰め
        # - ユーザーIDをハッシュ化
        # など

        logger.info("ユーザーデータの匿名化処理を実行")

        return True

    def get_privacy_settings(self):
        """プライバシー設定を取得"""
        return self.privacy_settings.copy()

    def export_user_data(self):
        """ユーザーデータをエクスポート"""
        # 実際のアプリでは、ここで各サービスからユーザーデータを収集してエクスポート
        user_data = {
            "user_profile": self.user_profile.get_profile(),
            "privacy_settings": self.privacy_settings
        }

        # 各サービスのデータを追加
        # ...

        return user_data
```

### プライバシー設定画面の実装

```python
# app/pages/privacy_settings_page.py
import flet as ft
import json
from app.services.privacy_service import PrivacyService

class PrivacySettingsPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.privacy_service = PrivacyService()

        # ページの初期化
        self.init_page()

    def init_page(self):
        """ページの初期化"""
        self.page.title = "プライバシー設定"

        # 現在の設定を取得
        settings = self.privacy_service.get_privacy_settings()
        consents = settings.get("consents", {})

        # 同意設定スイッチ
        analytics_switch = ft.Switch(
            label="アプリ使用状況の分析",
            value=consents.get("analytics", False),
            on_change=lambda e: self.on_consent_change("analytics", e.control.value)
        )

        crash_reports_switch = ft.Switch(
            label="クラッシュレポートの送信",
            value=consents.get("crash_reports", False),
            on_change=lambda e: self.on_consent_change("crash_reports", e.control.value)
        )

        personalization_switch = ft.Switch(
            label="パーソナライズ機能の利用",
            value=consents.get("personalization", False),
            on_change=lambda e: self.on_consent_change("personalization", e.control.value)
        )

        marketing_switch = ft.Switch(
            label="マーケティング目的での利用",
            value=consents.get("marketing", False),
            on_change=lambda e: self.on_consent_change("marketing", e.control.value)
        )

        # 一括同意/拒否ボタン
        consent_all_button = ft.ElevatedButton(
            "すべて許可",
            on_click=self.on_consent_all
        )

        refuse_all_button = ft.ElevatedButton(
            "すべて拒否",
            on_click=self.on_refuse_all,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.RED_400,
                color=ft.colors.WHITE
            )
        )

        # データ匿名化スイッチ
        anonymize_switch = ft.Switch(
            label="データを匿名化する",
            value=settings.get("anonymize_data", False),
            on_change=lambda e: self.on_anonymize_change(e.control.value)
        )

        # データアクセス/削除ボタン
        data_access_button = ft.ElevatedButton(
            "自分のデータにアクセスする",
            on_click=self.on_data_access_request
        )

        data_deletion_button = ft.ElevatedButton(
            "自分のデータを削除する",
            on_click=self.on_data_deletion_request,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.RED_400,
                color=ft.colors.WHITE
            )
        )

        # プライバシーポリシーリンク
        privacy_policy_link = ft.TextButton(
            "プライバシーポリシーを表示",
            on_click=lambda e: self.page.launch_url("https://example.com/privacy")
        )

        # レイアウト
        self.page.add(
            ft.Text("プライバシー設定", size=24, weight="bold"),
            ft.Text("以下の設定を変更することで、アプリでのデータ収集と利用方法を制御できます。"),

            ft.Container(
                padding=ft.padding.all(10),
                margin=ft.margin.only(top=10, bottom=10),
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                content=ft.Column([
                    ft.Text("データ収集の同意", size=18, weight="bold"),
                    analytics_switch,
                    crash_reports_switch,
                    personalization_switch,
                    marketing_switch,
                    ft.Row([
                        consent_all_button,
                        refuse_all_button
                    ])
                ])
            ),

            ft.Container(
                padding=ft.padding.all(10),
                margin=ft.margin.only(bottom=10),
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                content=ft.Column([
                    ft.Text("データの匿名化", size=18, weight="bold"),
                    ft.Text("オンにすると、収集されるデータから個人を特定できる情報が削除されます。"),
                    anonymize_switch
                ])
            ),

            ft.Container(
                padding=ft.padding.all(10),
                margin=ft.margin.only(bottom=10),
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                content=ft.Column([
                    ft.Text("データ管理", size=18, weight="bold"),
                    ft.Text("EUのGDPRやカリフォルニア州のCCPAなどのプライバシー法に基づく権利を行使できます。"),
                    data_access_button,
                    data_deletion_button
                ])
            ),

            privacy_policy_link
        )

    def on_consent_change(self, consent_type, value):
        """同意設定変更時の処理"""
        # 同意設定を更新
        self.privacy_service.update_consent(consent_type, value)

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"設定を更新しました: {consent_type} = {'有効' if value else '無効'}"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_consent_all(self, e):
        """すべて許可ボタンクリック時の処理"""
        # すべての同意設定を有効化
        consent_dict = {
            "analytics": True,
            "crash_reports": True,
            "personalization": True,
            "marketing": True
        }

        self.privacy_service.update_multiple_consents(consent_dict)

        # ページを再読み込み
        self.page.clean()
        self.init_page()

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("すべての設定を許可しました"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_refuse_all(self, e):
        """すべて拒否ボタンクリック時の処理"""
        # すべての同意設定を無効化
        consent_dict = {
            "analytics": False,
            "crash_reports": False,
            "personalization": False,
            "marketing": False
        }

        self.privacy_service.update_multiple_consents(consent_dict)

        # ページを再読み込み
        self.page.clean()
        self.init_page()

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("すべての設定を拒否しました"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_anonymize_change(self, value):
        """データ匿名化設定変更時の処理"""
        # 匿名化設定を更新
        self.privacy_service.set_anonymize_data(value)

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"データ匿名化: {'有効' if value else '無効'}"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_data_access_request(self, e):
        """データアクセス要求ボタンクリック時の処理"""
        # 確認ダイアログを表示
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("データアクセス要求"),
            content=ft.Text("アプリが収集したあなたのデータへのアクセスをリクエストします。処理には数日かかる場合があります。"),
            actions=[
                ft.TextButton("キャンセル", on_click=self.close_dialog),
                ft.TextButton("リクエスト", on_click=self.confirm_data_access)
            ]
        )
        self.page.dialog.open = True
        self.page.update()

    def on_data_deletion_request(self, e):
        """データ削除要求ボタンクリック時の処理"""
        # 確認ダイアログを表示
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("データ削除要求"),
            content=ft.Text("アプリが収集したあなたのデータの削除をリクエストします。この操作は元に戻せません。"),
            actions=[
                ft.TextButton("キャンセル", on_click=self.close_dialog),
                ft.TextButton("削除", on_click=self.confirm_data_deletion,
                             style=ft.ButtonStyle(color=ft.colors.RED))
            ]
        )
        self.page.dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """ダイアログを閉じる"""
        self.page.dialog.open = False
        self.page.update()

    def confirm_data_access(self, e):
        """データアクセス要求を確認"""
        # ダイアログを閉じる
        self.page.dialog.open = False

        # データアクセス要求を記録
        self.privacy_service.request_data_access()

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("データアクセス要求を送信しました。結果は登録されたメールアドレスに送信されます。"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def confirm_data_deletion(self, e):
        """データ削除要求を確認"""
        # ダイアログを閉じる
        self.page.dialog.open = False

        # データ削除要求を記録
        self.privacy_service.request_data_deletion()

        # 確認メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("データ削除要求を送信しました。処理完了後、確認メールが送信されます。"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()
```

### GDPR・CCPAコンプライアンスのためのポップアップ

```python
# app/components/privacy_consent_dialog.py
import flet as ft
from app.services.privacy_service import PrivacyService

class PrivacyConsentDialog(ft.UserControl):
    """プライバシー同意ダイアログ（GDPR・CCPA対応）"""

    def __init__(self, on_complete=None):
        super().__init__()
        self.privacy_service = PrivacyService()
        self.on_complete = on_complete

    def build(self):
        # スイッチコントロール
        self.analytics_switch = ft.Switch(
            label="アプリ使用状況の分析",
            value=True
        )

        self.crash_reports_switch = ft.Switch(
            label="クラッシュレポートの送信",
            value=True
        )

        self.personalization_switch = ft.Switch(
            label="パーソナライズ機能の利用",
            value=True
        )

        self.marketing_switch = ft.Switch(
            label="マーケティング目的での利用",
            value=False
        )

        # 同意ボタン
        consent_button = ft.ElevatedButton(
            "同意して続ける",
            on_click=self.on_consent
        )

        # 最小限ボタン
        minimal_button = ft.OutlinedButton(
            "必要最小限のみ許可",
            on_click=self.on_minimal
        )

        # メインコンテナ
        return ft.Container(
            width=400,
            height=480,
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            content=ft.Column([
                ft.Text("プライバシー設定", size=24, weight="bold"),
                ft.Text(
                    "当アプリはお客様に最適な体験を提供するために、以下の方法でデータを収集・利用します。"
                    "設定はいつでも変更できます。",
                    size=14
                ),
                ft.Divider(),

                ft.Container(
                    padding=ft.padding.all(10),
                    content=ft.Column([
                        self.analytics_switch,
                        ft.Text(
                            "アプリの使用状況を分析して、より良い機能を提供します。",
                            size=12,
                            color=ft.colors.GREY_700
                        )
                    ])
                ),

                ft.Container(
                    padding=ft.padding.all(10),
                    content=ft.Column([
                        self.crash_reports_switch,
                        ft.Text(
                            "アプリのクラッシュ情報を送信して、安定性を向上させます。",
                            size=12,
                            color=ft.colors.GREY_700
                        )
                    ])
                ),

                ft.Container(
                    padding=ft.padding.all(10),
                    content=ft.Column([
                        self.personalization_switch,
                        ft.Text(
                            "あなたの好みに合わせてコンテンツをパーソナライズします。",
                            size=12,
                            color=ft.colors.GREY_700
                        )
                    ])
                ),

                ft.Container(
                    padding=ft.padding.all(10),
                    content=ft.Column([
                        self.marketing_switch,
                        ft.Text(
                            "マーケティング目的でデータを利用します。",
                            size=12,
                            color=ft.colors.GREY_700
                        )
                    ])
                ),

                ft.Row([
                    consent_button,
                    minimal_button
                ], alignment=ft.MainAxisAlignment.CENTER),

                ft.TextButton(
                    "プライバシーポリシーを表示",
                    on_click=lambda e: self.page.launch_url("https://example.com/privacy")
                )
            ])
        )

    def on_consent(self, e):
        """同意ボタンクリック時の処理"""
        # 現在のスイッチの状態を取得
        consent_dict = {
            "analytics": self.analytics_switch.value,
            "crash_reports": self.crash_reports_switch.value,
            "personalization": self.personalization_switch.value,
            "marketing": self.marketing_switch.value
        }

        # 同意設定を更新
        self.privacy_service.update_multiple_consents(consent_dict)

        # 完了コールバックを呼び出し
        if self.on_complete:
            self.on_complete(True)

    def on_minimal(self, e):
        """最小限ボタンクリック時の処理"""
        # 必要最小限の設定
        consent_dict = {
            "analytics": False,
            "crash_reports": True,  # クラッシュレポートのみ有効
            "personalization": False,
            "marketing": False
        }

        # 同意設定を更新
        self.privacy_service.update_multiple_consents(consent_dict)

        # 完了コールバックを呼び出し
        if self.on_complete:
            self.on_complete(True)

# 使用例
def show_privacy_consent(page):
    """プライバシー同意ダイアログを表示"""
    # 既存のコンテンツを無効化
    for control in page.controls:
        control.disabled = True

    # オーバーレイ背景
    overlay = ft.Container(
        width=page.width,
        height=page.height,
        bgcolor=ft.colors.with_opacity(0.5, ft.colors.BLACK),
        alignment=ft.alignment.center
    )

    # ダイアログを作成
    dialog = PrivacyConsentDialog(
        on_complete=lambda result: remove_privacy_dialog(page, overlay, result)
    )

    # オーバーレイにダイアログを追加
    overlay.content = dialog

    # ページにオーバーレイを追加
    page.add(overlay)
    page.update()

def remove_privacy_dialog(page, overlay, result):
    """プライバシー同意ダイアログを削除"""
    # オーバーレイを削除
    page.controls.remove(overlay)

    # 既存のコンテンツを有効化
    for control in page.controls:
        control.disabled = False

    page.update()

    # 確認メッセージを表示
    page.snack_bar = ft.SnackBar(
        content=ft.Text("プライバシー設定を保存しました"),
        action="閉じる"
    )
    page.snack_bar.open = True
    page.update()
```

## 分析データの活用

収集したデータを効果的に活用するための方法と実装例を解説します。

### データダッシュボードの実装

```python
# app/pages/analytics_dashboard.py
import flet as ft
import time
import json
import random
from datetime import datetime, timedelta
from app.services.analytics import AnalyticsService
from app.services.event_tracker import EventTracker
from app.services.user_profile import UserProfileService
from app.services.performance import PerformanceMonitor

class AnalyticsDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.analytics = AnalyticsService()
        self.event_tracker = EventTracker()
        self.user_profile = UserProfileService()
        self.performance_monitor = PerformanceMonitor()

        # ページの初期化
        self.init_page()

    def init_page(self):
        """ページの初期化"""
        self.page.title = "分析ダッシュボード"

        # 時間範囲選択
        time_range_dropdown = ft.Dropdown(
            label="期間",
            width=200,
            options=[
                ft.dropdown.Option("day", "今日"),
                ft.dropdown.Option("week", "過去7日間"),
                ft.dropdown.Option("month", "過去30日間"),
                ft.dropdown.Option("year", "過去1年間")
            ],
            value="week",
            on_change=self.on_time_range_change
        )

        # 更新ボタン
        refresh_button = ft.ElevatedButton(
            "更新",
            icon=ft.icons.REFRESH,
            on_click=self.on_refresh
        )

        # KPIカード
        self.dau_card = self.create_kpi_card("DAU", "0", "デイリーアクティブユーザー")
        self.retention_card = self.create_kpi_card("リテンション", "0%", "7日間リテンション率")
        self.session_card = self.create_kpi_card("平均セッション", "0分", "セッション長")
        self.crash_card = self.create_kpi_card("クラッシュ率", "0%", "セッションあたり")

        # グラフタブ
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="ユーザー指標",
                    content=self.create_users_tab()
                ),
                ft.Tab(
                    text="エンゲージメント",
                    content=self.create_engagement_tab()
                ),
                ft.Tab(
                    text="パフォーマンス",
                    content=self.create_performance_tab()
                )
            ]
        )

        # レイアウト
        self.page.add(
            ft.Row([
                ft.Text("分析ダッシュボード", size=30, weight="bold"),
                ft.Spacer(),
                time_range_dropdown,
                refresh_button
            ]),

            ft.Row([
                self.dau_card,
                self.retention_card,
                self.session_card,
                self.crash_card
            ]),

            self.tabs
        )

        # 初回データ読み込み
        self.load_data("week")

    def create_kpi_card(self, title, value, subtitle):
        """KPIカードを作成"""
        return ft.Card(
            content=ft.Container(
                width=150,
                height=120,
                padding=ft.padding.all(10),
                content=ft.Column([
                    ft.Text(title, size=16, weight="bold"),
                    ft.Text(value, size=24, weight="bold"),
                    ft.Text(subtitle, size=12, color=ft.colors.GREY_700)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        )

    def create_users_tab(self):
        """ユーザー指標タブを作成"""
        # デモ用：実際のアプリではAPIからデータを取得
        chart_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("ユーザー数の推移", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        # セグメント分布
        segment_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("ユーザーセグメント分布", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        return ft.Column([
            chart_container,
            segment_container
        ])

    def create_engagement_tab(self):
        """エンゲージメントタブを作成"""
        # イベント分布
        events_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("イベント分布", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        # 画面別セッション時間
        screens_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("画面別セッション時間", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        return ft.Column([
            events_container,
            screens_container
        ])

    def create_performance_tab(self):
        """パフォーマンスタブを作成"""
        # CPU使用率
        cpu_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("CPU使用率", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        # メモリ使用量
        memory_container = ft.Container(
            width=800,
            height=300,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            padding=ft.padding.all(10),
            content=ft.Column([
                ft.Text("メモリ使用量", size=16, weight="bold"),
                ft.Text("読み込み中...", size=14)
            ])
        )

        return ft.Column([
            cpu_container,
            memory_container
        ])

    def on_time_range_change(self, e):
        """期間変更時の処理"""
        self.load_data(e.control.value)

    def on_refresh(self, e):
        """更新ボタンクリック時の処理"""
        # 現在選択されている期間を取得
        time_range = self.page.controls[0].controls[2].value

        # データを再読み込み
        self.load_data(time_range)

    def load_data(self, time_range):
        """指定された期間のデータを読み込み"""
        # プログレスインジケータの表示
        progress = ft.ProgressBar(width=800)
        self.page.add(progress)
        self.page.update()

        # デモ用：ランダムデータの生成
        # 実際のアプリでは、APIからデータを取得

        # KPIカードの更新
        dau_value = random.randint(1000, 10000)
        retention_value = random.randint(40, 90)
        session_value = random.randint(3, 15)
        crash_value = round(random.uniform(0.1, 5.0), 1)

        self.dau_card.content.content.controls[1].value = f"{dau_value:,}"
        self.retention_card.content.content.controls[1].value = f"{retention_value}%"
        self.session_card.content.content.controls[1].value = f"{session_value}分"
        self.crash_card.content.content.controls[1].value = f"{crash_value}%"

        # タブコンテンツの更新（デモのため、ダミーデータを使用）
        self.update_user_tab(time_range)
        self.update_engagement_tab(time_range)
        self.update_performance_tab(time_range)

        # プログレスインジケータを削除
        self.page.controls.remove(progress)

        # 更新完了メッセージを表示
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"データを更新しました（期間: {time_range}）"),
            action="閉じる"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def update_user_tab(self, time_range):
        """ユーザータブの更新"""
        # ユーザー数の推移チャート（デモ用ダミーデータ）
        chart_container = self.tabs.tabs[0].content.controls[0]

        # ダミーグラフの作成
        days = self.get_date_range(time_range)
        dau_values = [random.randint(1000, 10000) for _ in range(len(days))]
        mau_values = [random.randint(10000, 50000) for _ in range(len(days))]

        # ここで実際のグラフを作成（Fletの対応するコンポーネントを使用）
        chart_container.content = ft.Column([
            ft.Text("ユーザー数の推移", size=16, weight="bold"),
            ft.Text("※ デモデータ", italic=True, size=12),
            ft.Text(f"DAU: 平均 {sum(dau_values)/len(dau_values):,.0f} ユーザー", size=14),
            ft.Text(f"MAU: 平均 {sum(mau_values)/len(mau_values):,.0f} ユーザー", size=14),
            # 実際のアプリでは、ここにグラフコンポーネントを配置
        ])

        # セグメント分布
        segment_container = self.tabs.tabs[0].content.controls[1]

        # ダミーセグメントデータ
        segments = [
            {"name": "新規ユーザー", "percentage": random.randint(10, 30)},
            {"name": "リピーター", "percentage": random.randint(30, 50)},
            {"name": "パワーユーザー", "percentage": random.randint(10, 30)},
            {"name": "休眠ユーザー", "percentage": random.randint(5, 20)}
        ]

        # 表示用のリストビュー
        segment_items = []
        for segment in segments:
            segment_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(segment["name"], size=14),
                        ft.Text(f"{segment['percentage']}%", size=14),
                        ft.ProgressBar(width=300, value=segment["percentage"]/100)
                    ])
                )
            )

        segment_container.content = ft.Column([
            ft.Text("ユーザーセグメント分布", size=16, weight="bold"),
            ft.Text("※ デモデータ", italic=True, size=12),
            ft.Column(segment_items)
        ])

    def update_engagement_tab(self, time_range):
        """エンゲージメントタブの更新"""
        # イベント分布
        events_container = self.tabs.tabs[1].content.controls[0]

        # ダミーイベントデータ
        events = [
            {"name": "アプリ起動", "count": random.randint(5000, 20000)},
            {"name": "コンテンツ閲覧", "count": random.randint(3000, 15000)},
            {"name": "検索実行", "count": random.randint(1000, 8000)},
            {"name": "共有アクション", "count": random.randint(500, 3000)},
            {"name": "設定変更", "count": random.randint(200, 1000)}
        ]

        # 合計イベント数の計算
        total_events = sum(event["count"] for event in events)

        # 表示用のリストビュー
        event_items = []
        for event in events:
            percentage = event["count"] / total_events * 100
            event_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(event["name"], size=14),
                        ft.Text(f"{event['count']:,}回 ({percentage:.1f}%)", size=14),
                        ft.ProgressBar(width=300, value=percentage/100)
                    ])
                )
            )

        events_container.content = ft.Column([
            ft.Text("イベント分布", size=16, weight="bold"),
            ft.Text("※ デモデータ", italic=True, size=12),
            ft.Column(event_items)
        ])

        # 画面別セッション時間
        screens_container = self.tabs.tabs[1].content.controls[1]

        # ダミー画面データ
        screens = [
            {"name": "ホーム画面", "time": random.randint(60, 300)},
            {"name": "検索画面", "time": random.randint(30, 180)},
            {"name": "詳細画面", "time": random.randint(90, 360)},
            {"name": "設定画面", "time": random.randint(20, 120)},
            {"name": "プロフィール画面", "time": random.randint(30, 150)}
        ]

        # 表示用のリストビュー
        screen_items = []
        for screen in screens:
            screen_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(screen["name"], size=14),
                        ft.Text(f"{screen['time']}秒", size=14),
                        ft.ProgressBar(width=300, value=screen["time"]/360)  # 最大値を360秒と仮定
                    ])
                )
            )

        screens_container.content = ft.Column([
            ft.Text("画面別平均セッション時間", size=16, weight="bold"),
            ft.Text("※ デモデータ", italic=True, size=12),
            ft.Column(screen_items)
        ])

    def update_performance_tab(self, time_range):
        """パフォーマンスタブの更新"""
        # CPU使用率
        cpu_container = self.tabs.tabs[2].content.controls[0]

        # パフォーマンスモニタからデータを取得（実際のデータ）
        cpu_metrics = self.performance_monitor.get_metrics("cpu", limit=10)

        if cpu_metrics:
            # 実際のデータを表示
            cpu_values = [metric["value"] for metric in cpu_metrics]
            avg_cpu = sum(cpu_values) / len(cpu_values)
            max_cpu = max(cpu_values)

            cpu_container.content = ft.Column([
                ft.Text("CPU使用率", size=16, weight="bold"),
                ft.Text(f"平均: {avg_cpu:.1f}%", size=14),
                ft.Text(f"最大: {max_cpu:.1f}%", size=14)
            ])
        else:
            # ダミーデータ
            cpu_container.content = ft.Column([
                ft.Text("CPU使用率", size=16, weight="bold"),
                ft.Text("※ データがありません", italic=True, size=12)
            ])

        # メモリ使用量
        memory_container = self.tabs.tabs[2].content.controls[1]

        # パフォーマンスモニタからデータを取得（実際のデータ）
        memory_metrics = self.performance_monitor.get_metrics("memory", limit=10)

        if memory_metrics:
            # 実際のデータを表示
            memory_values = [metric["value"] for metric in memory_metrics]
            avg_memory = sum(memory_values) / len(memory_values)
            max_memory = max(memory_values)

            memory_container.content = ft.Column([
                ft.Text("メモリ使用量", size=16, weight="bold"),
                ft.Text(f"平均: {avg_memory:.1f}MB", size=14),
                ft.Text(f"最大: {max_memory:.1f}MB", size=14)
            ])
        else:
            # ダミーデータ
            memory_container.content = ft.Column([
                ft.Text("メモリ使用量", size=16, weight="bold"),
                ft.Text("※ データがありません", italic=True, size=12)
            ])

    def get_date_range(self, time_range):
        """指定された期間の日付リストを取得"""
        today = datetime.now()

        if time_range == "day":
            # 24時間（1時間ごと）
            return [(today - timedelta(hours=i)).strftime("%H:%M") for i in range(24, 0, -1)]
        elif time_range == "week":
            # 過去7日間
            return [(today - timedelta(days=i)).strftime("%m/%d") for i in range(7, 0, -1)]
        elif time_range == "month":
            # 過去30日間
            return [(today - timedelta(days=i)).strftime("%m/%d") for i in range(30, 0, -1)]
        elif time_range == "year":
            # 過去12ヶ月
            return [(today - timedelta(days=i*30)).strftime("%Y/%m") for i in range(12, 0, -1)]

        return []
```

この包括的なアプリ分析・モニタリングガイドを通じて、Python Fletアプリケーションで効果的な分析と監視を実装する方法を学びました。このガイドに含まれる実装例やベストプラクティスを活用することで、ユーザー行動の理解、パフォーマンスの最適化、そして継続的な改善のためのデータ駆動型の意思決定が可能になります。

プライバシーを尊重しながら有益なデータを収集・分析することで、ユーザーにとってより価値のある体験を提供しましょう。
