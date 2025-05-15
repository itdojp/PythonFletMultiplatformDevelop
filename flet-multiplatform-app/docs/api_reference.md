# API リファレンス

このドキュメントでは、アプリケーションで利用可能なAPIエンドポイントとその使用方法について説明します。

## 基本情報

- **ベースURL**: `http://localhost:8000/api/v1`
- **認証**: ベアラートークン認証を使用
- **レスポンス形式**: JSON

## 認証

### ログイン

ユーザー認証を行い、アクセストークンを取得します。

```http
POST /auth/login
```

**リクエストボディ:**

```json
{
  "username": "user@example.com",
  "password": "string"
}
```

**成功時のレスポンス (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## ユーザー

### ユーザー一覧の取得

ユーザーの一覧を取得します。管理者権限が必要です。

```http
GET /users/
```

**ヘッダー:**

```
Authorization: Bearer <access_token>
```

**成功時のレスポンス (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false
    }
  ],
  "total": 1
}
```

## アイテム

### アイテムの作成

新しいアイテムを作成します。

```http
POST /items/
```

**ヘッダー:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**リクエストボディ:**

```json
{
  "title": "新しいアイテム",
  "description": "これは新しいアイテムです"
}
```

**成功時のレスポンス (201 Created):**

```json
{
  "id": 1,
  "title": "新しいアイテム",
  "description": "これは新しいアイテムです",
  "owner_id": 1
}
```

## エラーレスポンス

### 400 Bad Request

リクエストが不正な場合に返されます。

```json
{
  "detail": "Invalid request"
}
```

### 401 Unauthorized

認証に失敗した場合に返されます。

```json
{
  "detail": "認証情報が無効です"
}
```

### 404 Not Found

リソースが見つからない場合に返されます。

```json
{
  "detail": "Item not found"
}
```

## レート制限

- 認証済みユーザー: 1分あたり60リクエスト
- 未認証ユーザー: 1分あたり10リクエスト
