# トラブルシューティング

このドキュメントでは、アプリケーションの開発・実行中に発生する可能性のある一般的な問題とその解決策を説明します。

## 目次

- [依存関係のエラー](#依存関係のエラー)
- [データベース接続の問題](#データベース接続の問題)
- [フロントエンドのビルドエラー](#フロントエンドのビルドエラー)
- [API接続の問題](#api接続の問題)
- [認証エラー](#認証エラー)

## 依存関係のエラー

### 問題: パッケージのバージョン競合

**エラーメッセージ例:**
```
ERROR: Cannot install -r requirements.txt and package==x.x.x because these package versions have conflicting dependencies.
```

**解決策:**
```bash
# 仮想環境をクリーンアップして再インストール
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または .\venv\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## データベース接続の問題

### 問題: データベース接続エラー

**エラーメッセージ例:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**解決策:**
1. データベースファイルへの書き込み権限を確認してください
2. データベースディレクトリが存在することを確認してください
3. `.env` ファイルの `DATABASE_URL` が正しいことを確認してください

## フロントエンドのビルドエラー

### 問題: Node.js の依存関係エラー

**エラーメッセージ例:**
```
Module not found: Error: Can't resolve 'module-name'
```

**解決策:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## API接続の問題

### 問題: CORS エラー

**エラーメッセージ例:**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**解決策:**
バックエンドのCORS設定を確認し、フロントエンドのオリジンが許可されていることを確認してください。

## 認証エラー

### 問題: トークンが無効または期限切れ

**エラーメッセージ例:**
```
{"detail":"認証情報が無効です"}
```

**解決策:**
1. トークンの有効期限を確認してください
2. 再度ログインして新しいトークンを取得してください
3. トークンが正しくヘッダーに含まれていることを確認してください
   ```
   Authorization: Bearer <your-token>
   ```

## サポート

上記の解決策で問題が解決しない場合は、以下の情報を添えてイシューを登録してください：

1. エラーメッセージの全文
2. 再現手順
3. 環境情報（OS、Pythonバージョン、Node.jsバージョンなど）
4. 関連するコードスニペット
