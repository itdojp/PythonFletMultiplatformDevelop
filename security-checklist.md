# Python Flet - セキュリティチェックリスト

このチェックリストは、Python Fletで開発するマルチプラットフォームアプリケーションにおいて、セキュリティを確保するための重要な考慮事項とベストプラクティスをまとめたものです。アプリケーション開発の各段階で参照し、セキュリティリスクを最小限に抑えるようにしましょう。

## 目次

1. [認証とアクセス制御](#認証とアクセス制御)
2. [データ保護と暗号化](#データ保護と暗号化)
3. [入力バリデーションとサニタイズ](#入力バリデーションとサニタイズ)
4. [API通信のセキュリティ](#api通信のセキュリティ)
5. [ローカルストレージのセキュリティ](#ローカルストレージのセキュリティ)
6. [依存関係の管理](#依存関係の管理)
7. [プラットフォーム固有のセキュリティ対策](#プラットフォーム固有のセキュリティ対策)
8. [セキュリティテスト](#セキュリティテスト)
9. [ログとモニタリング](#ログとモニタリング)
10. [セキュリティ対策実装例](#セキュリティ対策実装例)

## 認証とアクセス制御

ユーザー認証とアクセス権限に関するセキュリティ対策:

### 認証システムの実装
- [ ] 強力なパスワードポリシーを適用する（最小長、複雑さ要件）
- [ ] 多要素認証（MFA/2FA）のサポートを検討する
- [ ] パスワードハッシュ化には強固なアルゴリズム（bcrypt, Argon2）を使用する
- [ ] ログイン試行回数を制限し、ブルートフォース攻撃を防止する
- [ ] ユーザーセッションの適切な管理（有効期限、更新メカニズム）
- [ ] セキュアなパスワードリセット機能（ワンタイムトークン、有効期限）

### トークンベース認証のベストプラクティス
- [ ] JWTなどのセキュアなトークン形式を使用する
- [ ] トークンに適切な有効期限を設定する
- [ ] トークンのリフレッシュメカニズムを実装する
- [ ] トークンの署名検証を確実に行う
- [ ] 機密情報をトークンに含めない
- [ ] トークンの安全な保存（Webの場合はHTTPOnly Cookie）

### アクセス制御
- [ ] 適切な認可（Authorization）メカニズムを実装する
- [ ] ロールベースアクセス制御（RBAC）またはアクセス制御リスト（ACL）の導入
- [ ] UIコンポーネントレベルでのアクセス制御を適用する
- [ ] サーバーサイドでのアクセス制御の二重チェックを実施する
- [ ] 垂直的（ロール階層）および水平的（同一ロール内での制限）アクセス制御を適用する

## データ保護と暗号化

機密データの保護と暗号化のベストプラクティス:

### アプリ内データの暗号化
- [ ] ローカルに保存される重要なデータを暗号化する
- [ ] アプリケーションのプライベートキーや暗号化キーの安全な管理
- [ ] メモリ内の機密データの最小化と保持時間の制限
- [ ] 適切な暗号化アルゴリズム（AES-256など）とモード（GCM、CBC）の選択
- [ ] キーのローテーションメカニズムの実装

### 機密データの取り扱い
- [ ] パスワードやトークンなどの機密情報をログに記録しない
- [ ] デバッグ出力での機密情報の表示を防止する
- [ ] クリップボードへの機密情報の自動コピーを防止する
- [ ] 画面キャプチャ時の機密情報保護（iOSのisSecureTextEntryなど）
- [ ] アプリの切り替え時に機密情報を画面から消去する

### データのバックアップと削除
- [ ] バックアップデータの暗号化
- [ ] ユーザーデータの完全削除機能（アカウント削除時）
- [ ] キャッシュデータの定期的なクリーンアップ
- [ ] セッション終了時の一時データの適切な破棄

## 入力バリデーションとサニタイズ

ユーザー入力の安全な処理:

### 入力バリデーション
- [ ] すべてのユーザー入力に対する適切なバリデーションを実施する
- [ ] クライアント側だけでなく、サーバー側でもバリデーションを行う
- [ ] 入力の長さ、形式、範囲、型のチェックを行う
- [ ] 正規表現を使用した入力パターンの検証
- [ ] バリデーションエラー時の適切なフィードバックを提供する

### 入力サニタイズ
- [ ] HTML/JavaScript注入を防ぐためのサニタイズ処理
- [ ] SQLインジェクションを防ぐためのパラメータ化クエリの使用
- [ ] ファイルアップロード時のファイル型、サイズ、内容の検証
- [ ] 外部からのデータをそのまま表示しない（XSSの防止）
- [ ] URLパラメータやディープリンクの検証とサニタイズ

### エスケープと表示
- [ ] HTML表示前のエスケープ処理
- [ ] JSON処理前のエスケープと検証
- [ ] ファイルパスやコマンドラインパラメータのサニタイズ

## API通信のセキュリティ

API呼び出しとネットワーク通信のセキュリティ:

### HTTPS通信
- [ ] すべてのネットワーク通信にHTTPSを使用する
- [ ] SSL/TLS証明書の検証を無効化しない
- [ ] SSLピンニングの実装を検討する
- [ ] 最新のTLSバージョン（TLS 1.2以上）を使用する
- [ ] 安全でない暗号スイートの無効化

### APIセキュリティ
- [ ] API呼び出しに認証トークンを適切に使用する
- [ ] トークンの有効期限と更新メカニズムの実装
- [ ] 機密パラメータをURLに含めない（POSTパラメータまたはヘッダーを使用）
- [ ] レスポンスの整合性検証（改ざん検出）
- [ ] レート制限とスロットリングの実装

### エラーハンドリング
- [ ] 適切なエラーハンドリングとユーザーへのフィードバック
- [ ] デバッグ情報や詳細なエラースタックトレースを本番環境で表示しない
- [ ] API通信エラー時のリトライ戦略と回復メカニズム
- [ ] 接続の脆弱性（中間者攻撃など）を検出する仕組み

## ローカルストレージのセキュリティ

デバイス上のデータ保存のセキュリティ:

### ストレージオプションの選択
- [ ] プラットフォーム推奨のセキュアストレージを使用する（iOSのKeychain、AndroidのEncrypted Shared Preferences）
- [ ] 機密データをプレーンテキストで保存しない
- [ ] ストレージアクセスの権限を最小限に制限する
- [ ] 一時ファイルの適切な処理とクリーンアップ

### データ分類と保護
- [ ] データの重要度に応じた保護レベルの設定（通常、機密、高機密）
- [ ] データの種類に基づく適切なストレージ方法の選択
- [ ] 機密データのキャッシュへの保存を避ける
- [ ] バックアップからの機密データの除外（適切なフラグ設定）

### 権限の最小化
- [ ] 必要最小限のファイルシステム権限でのアクセス
- [ ] 自動補完やスクリーンショットからの機密データの保護
- [ ] サードパーティによるデータアクセスの制限
- [ ] アプリ内でのファイルアクセス権限の管理

## 依存関係の管理

サードパーティライブラリとパッケージのセキュリティ:

### 依存パッケージの管理
- [ ] 使用する依存パッケージの最小化
- [ ] 依存パッケージの定期的な更新
- [ ] セキュリティ脆弱性のあるパッケージのチェックと更新
- [ ] 依存関係のロックファイルによるバージョン固定

### 脆弱性のスキャン
- [ ] 依存パッケージの脆弱性スキャンの自動化（safety, pip-audit, dependabotなど）
- [ ] CI/CDパイプラインでのセキュリティスキャンの統合
- [ ] 脆弱性データベース（CVE, NVD）との連携
- [ ] 重大な脆弱性が見つかった場合の緊急対応プロセス

### コード監査
- [ ] サードパーティライブラリのコードレビュー
- [ ] ライブラリのライセンスコンプライアンスチェック
- [ ] ライブラリが収集する可能性のあるデータの確認
- [ ] プラグインアーキテクチャでの安全なコード読み込み

## プラットフォーム固有のセキュリティ対策

各プラットフォームに特化したセキュリティ対策:

### Androidセキュリティ
- [ ] AndroidマニフェストでのMinSDKVersionとTargetSDKVersionの適切な設定
- [ ] アプリ署名と署名検証の実装
- [ ] Android Keystoreシステムを使用した暗号化キーの保存
- [ ] Android Protected Confirmationの使用（機密トランザクション）
- [ ] アクセス権限の最小化と実行時の権限要求
- [ ] ROOT検出による追加セキュリティ対策
- [ ] ProGuardやR8によるコード難読化

### iOSセキュリティ
- [ ] iOSキーチェーンの適切な使用
- [ ] App Transport Security (ATS)の有効化
- [ ] Data Protectionエンティトルメントの設定
- [ ] 生体認証（Face ID/Touch ID）の適切な実装
- [ ] AppサンドボックスとApp Groupsの適切な設定
- [ ] JailBreak検出による追加セキュリティ対策
- [ ] Swift/Objective-Cコードの難読化

### Webセキュリティ
- [ ] 適切なCORSヘッダーの設定
- [ ] Content Security Policy (CSP)の実装
- [ ] HTTP Strict Transport Security (HSTS)の有効化
- [ ] クロスサイトスクリプティング(XSS)防止
- [ ] クロスサイトリクエストフォージェリ(CSRF)対策
- [ ] セキュアなクッキー設定（HTTPOnly, Secure, SameSite）
- [ ] ローカルストレージとセッションストレージの適切な使用

## セキュリティテスト

アプリケーションの脆弱性テスト:

### セキュリティテスト計画
- [ ] セキュリティテストの範囲と頻度の定義
- [ ] セキュリティテスト担当者の指定
- [ ] リスクに基づいたテスト優先度の設定
- [ ] セキュリティテスト結果の評価基準の定義

### 自動セキュリティテスト
- [ ] 静的アプリケーションセキュリティテスト（SAST）の実施
- [ ] 動的アプリケーションセキュリティテスト（DAST）の実施
- [ ] モバイルアプリセキュリティテストフレームワークの使用
- [ ] 依存関係の脆弱性スキャンの自動化
- [ ] CI/CDパイプラインでのセキュリティテストの統合

### ペネトレーションテスト
- [ ] 定期的なペネトレーションテストの実施
- [ ] OWASP Mobile Top 10に基づくテスト
- [ ] セキュリティ専門家による手動テストの実施
- [ ] 発見された脆弱性の修正と再テスト

## ログとモニタリング

セキュリティイベントの検出と対応:

### セキュアなログ実装
- [ ] 機密情報をログに記録しない
- [ ] セキュリティイベントの適切なログ記録
- [ ] ログの改ざん防止策
- [ ] 必要に応じたログの暗号化
- [ ] ログローテーションと保存期間の設定

### セキュリティモニタリング
- [ ] 異常なアクティビティの検出（多数のログイン失敗など）
- [ ] 不審なAPIリクエストのモニタリング
- [ ] デバイスとの通信喪失の検出
- [ ] クラッシュレポートの分析
- [ ] ユーザーからのセキュリティ問題報告の収集

### インシデント対応
- [ ] セキュリティインシデント対応計画の策定
- [ ] アプリのリモート無効化/更新メカニズム
- [ ] ユーザーへのセキュリティ通知メカニズム
- [ ] 緊急パッチのデプロイ戦略

## セキュリティ対策実装例

実際のコードサンプルによるセキュリティ対策の実装:

### 安全なAPIクライアント

```python
# /app/data/api/secure_api_client.py
import httpx
import json
import time
import hashlib
import os
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.security.token_manager import TokenManager

class SecureApiClient:
    def __init__(self, token_manager: TokenManager):
        self.base_url = settings.API_BASE_URL
        self.timeout = settings.API_TIMEOUT
        self.token_manager = token_manager
        
        # 共通ヘッダー
        self.common_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}"
        }
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET リクエストを送信"""
        url = f"{self.base_url}{endpoint}"
        
        # 認証ヘッダーを取得
        headers = await self._get_auth_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # HTTPSの検証を必ず有効化
            response = await client.get(
                url, 
                params=params, 
                headers={**self.common_headers, **headers},
                verify=True  # SSL検証を強制
            )
            
            return await self._handle_response(response)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST リクエストを送信"""
        url = f"{self.base_url}{endpoint}"
        
        # 認証ヘッダーを取得
        headers = await self._get_auth_headers()
        
        # リクエストIDを生成（重複リクエスト防止）
        request_id = self._generate_request_id()
        headers["X-Request-ID"] = request_id
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url, 
                json=data, 
                headers={**self.common_headers, **headers},
                verify=True
            )
            
            return await self._handle_response(response)
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT リクエストを送信"""
        url = f"{self.base_url}{endpoint}"
        
        # 認証ヘッダーを取得
        headers = await self._get_auth_headers()
        
        # リクエストIDを生成
        request_id = self._generate_request_id()
        headers["X-Request-ID"] = request_id
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                url, 
                json=data, 
                headers={**self.common_headers, **headers},
                verify=True
            )
            
            return await self._handle_response(response)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE リクエストを送信"""
        url = f"{self.base_url}{endpoint}"
        
        # 認証ヘッダーを取得
        headers = await self._get_auth_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                url, 
                headers={**self.common_headers, **headers},
                verify=True
            )
            
            return await self._handle_response(response)
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """認証ヘッダーを取得"""
        headers = {}
        
        # アクセストークンが存在する場合は追加
        token = await self.token_manager.get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # APIキー認証（必要な場合）
        if hasattr(settings, "API_KEY") and settings.API_KEY:
            headers["X-API-Key"] = settings.API_KEY
        
        return headers
    
    async def _handle_response(self, response):
        """レスポンスを処理"""
        if response.status_code >= 200 and response.status_code < 300:
            # 成功レスポンス
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"success": True, "data": response.text}
        elif response.status_code == 401:
            # 認証エラー - トークンのリフレッシュを試みる
            if await self._refresh_and_retry(response):
                return True
            raise ApiAuthException("Authentication failed", response.status_code)
        else:
            # その他のエラー
            self._handle_error_response(response)
    
    async def _refresh_and_retry(self, response):
        """トークンをリフレッシュして再試行"""
        # トークンリフレッシュを試みる
        refresh_success = await self.token_manager.refresh_token()
        
        if refresh_success:
            # 原リクエストの情報を取得
            original_request = response.request
            
            # 新しいトークンでヘッダーを更新
            headers = dict(original_request.headers)
            token = await self.token_manager.get_access_token()
            headers["Authorization"] = f"Bearer {token}"
            
            # リクエストを再実行
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                new_response = await client.send(
                    original_request.copy_with(headers=headers)
                )
                
                # 再試行結果を処理
                if new_response.status_code >= 200 and new_response.status_code < 300:
                    try:
                        return new_response.json()
                    except json.JSONDecodeError:
                        return {"success": True, "data": new_response.text}
        
        return False
    
    def _handle_error_response(self, response):
        """エラーレスポンスを処理"""
        error_data = {"status_code": response.status_code}
        
        try:
            error_body = response.json()
            error_data.update(error_body)
        except json.JSONDecodeError:
            error_data["message"] = response.text
        
        # ステータスコードに基づいて適切な例外を発生
        if response.status_code == 400:
            raise ApiBadRequestException(error_data)
        elif response.status_code == 403:
            raise ApiForbiddenException(error_data)
        elif response.status_code == 404:
            raise ApiNotFoundException(error_data)
        elif response.status_code == 422:
            raise ApiValidationException(error_data)
        elif response.status_code >= 500:
            raise ApiServerException(error_data)
        else:
            raise ApiException(error_data)
    
    def _generate_request_id(self) -> str:
        """一意のリクエストIDを生成"""
        # タイムスタンプとランダム文字列を組み合わせて一意のIDを生成
        timestamp = str(int(time.time() * 1000))
        random_bytes = os.urandom(8)
        random_hex = random_bytes.hex()
        
        # ハッシュ化して短縮
        request_id = hashlib.sha256(f"{timestamp}{random_hex}".encode()).hexdigest()[:16]
        return request_id

# APIエラー例外クラス
class ApiException(Exception):
    """一般的なAPIエラー"""
    def __init__(self, error_data):
        self.error_data = error_data
        self.status_code = error_data.get("status_code", 500)
        self.message = error_data.get("message", "Unknown API error")
        super().__init__(self.message)

class ApiAuthException(ApiException):
    """認証エラー"""
    pass

class ApiBadRequestException(ApiException):
    """リクエスト形式エラー"""
    pass

class ApiForbiddenException(ApiException):
    """アクセス権限エラー"""
    pass

class ApiNotFoundException(ApiException):
    """リソース不在エラー"""
    pass

class ApiValidationException(ApiException):
    """バリデーションエラー"""
    pass

class ApiServerException(ApiException):
    """サーバーエラー"""
    pass
```

### セキュアなトークン管理

```python
# /app/core/security/token_manager.py
import time
import json
from typing import Dict, Any, Optional
from app.core.storage.secure_storage import SecureStorage

class TokenManager:
    def __init__(self, secure_storage: SecureStorage):
        self.secure_storage = secure_storage
        self.token_key = "auth_tokens"
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        
        # トークン更新のコールバック
        self.token_refresh_callback = None
    
    async def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        """トークンを設定して保存"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = int(time.time()) + expires_in
        
        # トークンの安全な保存
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": self.token_expiry
        }
        
        # 暗号化して保存
        await self.secure_storage.set_secure_item(self.token_key, json.dumps(token_data))
    
    async def get_access_token(self) -> Optional[str]:
        """アクセストークンを取得（必要に応じてロード）"""
        # メモリ上にない場合はストレージからロード
        if not self.access_token:
            await self._load_tokens()
        
        # トークンの期限切れをチェック
        if self.access_token and self._is_token_expired():
            # 期限切れの場合は更新を試みる
            if self.refresh_token:
                refresh_success = await self.refresh_token()
                if not refresh_success:
                    return None
            else:
                return None
        
        return self.access_token
    
    async def refresh_token(self) -> bool:
        """リフレッシュトークンを使用してアクセストークンを更新"""
        if not self.refresh_token:
            return False
        
        try:
            # トークン更新のコールバックが設定されている場合は呼び出し
            if self.token_refresh_callback:
                result = await self.token_refresh_callback(self.refresh_token)
                
                if result and result.get("success"):
                    # 新しいトークンを設定
                    new_tokens = result.get("tokens", {})
                    await self.set_tokens(
                        new_tokens.get("access_token"),
                        new_tokens.get("refresh_token", self.refresh_token),
                        new_tokens.get("expires_in", 3600)
                    )
                    return True
            
            return False
        except Exception as e:
            print(f"Token refresh error: {e}")
            return False
    
    async def clear_tokens(self):
        """トークンを消去"""
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = 0
        
        # ストレージからも削除
        await self.secure_storage.delete_secure_item(self.token_key)
    
    async def _load_tokens(self):
        """ストレージからトークンをロード"""
        token_json = await self.secure_storage.get_secure_item(self.token_key)
        
        if token_json:
            try:
                token_data = json.loads(token_json)
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_expiry = token_data.get("expires_at", 0)
            except json.JSONDecodeError:
                # トークンデータの破損
                await self.clear_tokens()
    
    def _is_token_expired(self) -> bool:
        """トークンが期限切れかどうかをチェック"""
        # 有効期限の30秒前に期限切れと判断（猶予期間）
        return int(time.time()) > (self.token_expiry - 30)
    
    def set_token_refresh_callback(self, callback):
        """トークン更新のコールバックを設定"""
        self.token_refresh_callback = callback
```

### セキュアなストレージ

```python
# /app/core/storage/secure_storage.py
import base64
import os
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.platform.storage.storage_interface import StorageInterface

class SecureStorage:
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.prefix = "secure_"
        
        # 暗号化キーの初期化
        self._initialize_encryption_key()
    
    async def set_secure_item(self, key: str, value: str) -> bool:
        """データを暗号化して保存"""
        if not value:
            return await self.delete_secure_item(key)
        
        try:
            # データを暗号化
            encrypted_data = self._encrypt(value.encode('utf-8'))
            
            # Base64エンコードして保存（バイナリデータを文字列として保存するため）
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            
            # ストレージに保存
            return await self.storage.set(f"{self.prefix}{key}", encoded_data)
        except Exception as e:
            print(f"Secure storage encryption error: {e}")
            return False
    
    async def get_secure_item(self, key: str) -> Optional[str]:
        """保存された暗号化データを復号化して取得"""
        try:
            # ストレージからデータを取得
            encoded_data = await self.storage.get(f"{self.prefix}{key}")
            
            if not encoded_data:
                return None
            
            # Base64デコード
            encrypted_data = base64.b64decode(encoded_data)
            
            # データを復号化
            decrypted_data = self._decrypt(encrypted_data)
            
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"Secure storage decryption error: {e}")
            return None
    
    async def delete_secure_item(self, key: str) -> bool:
        """保存されたデータを削除"""
        return await self.storage.delete(f"{self.prefix}{key}")
    
    def _initialize_encryption_key(self):
        """暗号化キーを初期化（または取得）"""
        # デバイス固有の識別子またはアプリ固有の識別子を使用
        # 注: 実際のアプリではより安全なキー管理が必要
        device_id = self._get_device_id()
        
        # ソルトは固定値または設定から取得（アプリインストール間で一貫性が必要）
        salt = b"secure_storage_salt_value"
        
        # PBKDF2を使用してキーを導出
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256のキー長
            salt=salt,
            iterations=100000,  # 十分な反復回数
        )
        
        self.encryption_key = kdf.derive(device_id.encode('utf-8'))
    
    def _encrypt(self, data: bytes) -> bytes:
        """AES-GCMでデータを暗号化"""
        # ノンスを生成（毎回異なる値）
        nonce = os.urandom(12)
        
        # AES-GCM暗号化器を初期化
        aesgcm = AESGCM(self.encryption_key)
        
        # データを暗号化（認証タグ付き）
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        # ノンスと暗号文を連結して返す
        return nonce + ciphertext
    
    def _decrypt(self, data: bytes) -> bytes:
        """AES-GCMでデータを復号化"""
        # ノンスを取得（最初の12バイト）
        nonce = data[:12]
        
        # 暗号文を取得（残りのバイト）
        ciphertext = data[12:]
        
        # AES-GCM復号化器を初期化
        aesgcm = AESGCM(self.encryption_key)
        
        # データを復号化
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    def _get_device_id(self) -> str:
        """デバイス固有の識別子を取得（または生成）"""
        # 注: プラットフォームによって適切な方法で実装
        # ここでは簡略化のためにダミー値を返す
        return "secure_device_identifier_value"
```

### セキュアなパスワードバリデーション

```python
# /app/core/security/password_validator.py
import re
from typing import Dict, List, Tuple

class PasswordValidator:
    def __init__(self):
        # パスワード要件の設定
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digit = True
        self.require_special_char = True
        self.max_length = 128
        
        # 特殊文字の定義
        self.special_chars = r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]"
        
        # 一般的なパスワードのブラックリスト
        self.password_blacklist = [
            "password", "123456", "qwerty", "admin", "welcome",
            "password123", "12345678", "letmein", "iloveyou"
        ]
    
    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """パスワードを検証し、有効かどうかとエラーメッセージを返す"""
        errors = []
        
        # 長さのチェック
        if len(password) < self.min_length:
            errors.append(f"パスワードは少なくとも{self.min_length}文字必要です")
        
        if len(password) > self.max_length:
            errors.append(f"パスワードは{self.max_length}文字以下である必要があります")
        
        # 大文字のチェック
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("パスワードには少なくとも1つの大文字が必要です")
        
        # 小文字のチェック
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("パスワードには少なくとも1つの小文字が必要です")
        
        # 数字のチェック
        if self.require_digit and not re.search(r"\d", password):
            errors.append("パスワードには少なくとも1つの数字が必要です")
        
        # 特殊文字のチェック
        if self.require_special_char and not re.search(self.special_chars, password):
            errors.append("パスワードには少なくとも1つの特殊文字が必要です")
        
        # 一般的なパスワードのチェック
        if password.lower() in self.password_blacklist:
            errors.append("このパスワードは一般的すぎるため使用できません")
        
        # パスワードに個人情報が含まれていないかのチェック
        # 注: 実際のアプリでは、ユーザー名や氏名などの個人情報をチェック
        
        return len(errors) == 0, errors
    
    def get_password_strength(self, password: str) -> Dict[str, any]:
        """パスワードの強度を評価"""
        # 基本強度（0-100）
        strength = 0
        feedback = []
        
        # 長さによる強度ボーナス（最大50ポイント）
        length_bonus = min(50, len(password) * 2)
        strength += length_bonus
        
        # 文字種類による強度ボーナス
        if re.search(r"[A-Z]", password):
            strength += 10
        else:
            feedback.append("大文字を追加すると強度が向上します")
        
        if re.search(r"[a-z]", password):
            strength += 10
        else:
            feedback.append("小文字を追加すると強度が向上します")
        
        if re.search(r"\d", password):
            strength += 10
        else:
            feedback.append("数字を追加すると強度が向上します")
        
        if re.search(self.special_chars, password):
            strength += 20
        else:
            feedback.append("特殊文字を追加すると強度が向上します")
        
        # 一般的なパスワードのペナルティ
        if password.lower() in self.password_blacklist:
            strength = max(0, strength - 50)
            feedback.append("このパスワードは一般的すぎるため危険です")
        
        # 強度レベルの決定
        strength_level = "weak"
        if strength >= 80:
            strength_level = "strong"
        elif strength >= 50:
            strength_level = "medium"
        
        return {
            "score": strength,
            "level": strength_level,
            "feedback": feedback
        }
```

### 入力サニタイズと検証

```python
# /app/core/security/input_validator.py
import re
import html
from typing import Dict, Any, List, Tuple, Optional, Union

class InputValidator:
    def __init__(self):
        # 共通の正規表現パターン
        self.patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "username": r"^[a-zA-Z0-9_-]{3,20}$",
            "name": r"^[a-zA-Z\s'-]{2,50}$",
            "phone": r"^\+?[0-9\s-()]{8,20}$",
            "zipcode": r"^[0-9]{5}(-[0-9]{4})?$",
            "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
        }
    
    def validate_field(self, field_type: str, value: str) -> Tuple[bool, Optional[str]]:
        """指定されたタイプのフィールドを検証"""
        if field_type in self.patterns:
            pattern = self.patterns[field_type]
            if re.match(pattern, value):
                return True, None
            else:
                return False, f"Invalid {field_type} format"
        
        # 未知のフィールドタイプ
        return False, "Unknown field type"
    
    def validate_form(self, form_data: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """フォームデータを検証"""
        errors = {}
        
        for field, field_rules in rules.items():
            field_value = form_data.get(field, "")
            field_errors = []
            
            # 必須フィールドのチェック
            if field_rules.get("required", False) and not field_value:
                field_errors.append("This field is required")
                errors[field] = field_errors
                continue
            
            # 空の非必須フィールドはスキップ
            if not field_value and not field_rules.get("required", False):
                continue
            
            # 型チェック
            field_type = field_rules.get("type")
            if field_type:
                is_valid, error_msg = self.validate_field(field_type, field_value)
                if not is_valid:
                    field_errors.append(error_msg)
            
            # 最小長チェック
            min_length = field_rules.get("min_length")
            if min_length is not None and len(field_value) < min_length:
                field_errors.append(f"Minimum length is {min_length} characters")
            
            # 最大長チェック
            max_length = field_rules.get("max_length")
            if max_length is not None and len(field_value) > max_length:
                field_errors.append(f"Maximum length is {max_length} characters")
            
            # カスタムバリデーション
            custom_validator = field_rules.get("validator")
            if custom_validator and callable(custom_validator):
                custom_result = custom_validator(field_value)
                if custom_result is not True:
                    field_errors.append(custom_result)
            
            # 一致チェック
            match_field = field_rules.get("match")
            if match_field and match_field in form_data:
                if field_value != form_data[match_field]:
                    field_errors.append(f"Does not match with {match_field}")
            
            # エラーがあれば追加
            if field_errors:
                errors[field] = field_errors
        
        return errors
    
    def sanitize_html(self, value: str) -> str:
        """HTMLをサニタイズ（XSS対策）"""
        return html.escape(value)
    
    def sanitize_sql(self, value: str) -> str:
        """SQLインジェクション対策のサニタイズ"""
        # 基本的なSQLインジェクション対策
        # 注: 実際のアプリではパラメータ化クエリを使用すべき
        dangerous_chars = ["'", "\"", ";", "--", "/*", "*/", "xp_"]
        result = value
        for char in dangerous_chars:
            result = result.replace(char, "")
        return result
    
    def sanitize_input(self, value: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """入力値を再帰的にサニタイズ"""
        if isinstance(value, str):
            return self.sanitize_html(value)
        elif isinstance(value, dict):
            return {k: self.sanitize_input(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.sanitize_input(v) for v in value]
        else:
            return value
```

### セキュリティヘッダーの設定（Web版）

```python
# /app/platform/web/security_headers.py
from typing import Dict

def get_security_headers() -> Dict[str, str]:
    """Web版アプリのセキュリティヘッダーを取得"""
    return {
        # Content-Security-Policy: スクリプトやリソースの読み込み元を制限
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' https://api.example.com; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-src 'none'"
        ),
        # XSS-Protection: ブラウザのXSS対策を有効化
        "X-XSS-Protection": "1; mode=block",
        # Content-Type-Options: MIMEタイプのスニッフィングを防止
        "X-Content-Type-Options": "nosniff",
        # Frame-Options: クリックジャッキング対策
        "X-Frame-Options": "DENY",
        # Referrer-Policy: リファラー情報の送信を制限
        "Referrer-Policy": "strict-origin-when-cross-origin",
        # Feature-Policy: 特定の機能へのアクセスを制限
        "Feature-Policy": (
            "microphone 'none'; "
            "camera 'none'; "
            "geolocation 'self'"
        ),
        # Strict-Transport-Security: HTTPS接続の強制
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }

def apply_security_headers(response):
    """レスポンスにセキュリティヘッダーを適用"""
    headers = get_security_headers()
    for key, value in headers.items():
        response.headers[key] = value
    return response

def setup_web_security(app):
    """Webアプリケーションにセキュリティ設定を適用"""
    # 注: フレームワーク依存の実装
    # Flaskの例
    if hasattr(app, 'after_request'):
        @app.after_request
        def add_security_headers(response):
            return apply_security_headers(response)
```

このセキュリティチェックリストに従うことで、Python Fletアプリケーションのセキュリティを大幅に向上させることができます。すべてのプラットフォームに共通するセキュリティ対策と、各プラットフォーム固有の対策を組み合わせて実装することで、ユーザーデータを保護し、アプリケーションに対する様々な攻撃を防止しましょう。開発の初期段階からセキュリティを考慮することで、後からの修正コストを削減し、ユーザーの信頼を獲得することができます。