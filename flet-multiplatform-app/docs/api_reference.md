# API リファレンス

このドキュメントでは、アプリケーションで利用可能なAPIエンドポイントとその使用方法について説明します。

## 基本情報

- **ベースURL**: `http://localhost:8000/api/v1` (ポートは設定により`8001`等に変更される場合があります)
- **認証**: 基本的にベアラートークン認証（OAuth2準拠）を使用します。各エンドポイントの説明に認証が必要か記載しています。
  *(注意: 現在、一部エンドポイントで認証機構の実装がTODOとなっている可能性があります。ドキュメントは意図された動作を記載しています。)*
- **レスポンス形式**: JSON

## スキーマ定義 (主要なもの)

APIで使用される主要なデータ構造です。

### Token

アクセストークン情報。

```json
{
  "access_token": "string (JWT)",
  "token_type": "string (bearer)"
}
```

### UserBase

ユーザー情報の基本形。

```json
{
  "email": "string (user@example.com)",
  "username": "string"
}
```

### UserCreate (UserBase を継承)

ユーザー作成時のリクエスト。

```json
{
  "email": "string (user@example.com)",
  "username": "string",
  "password": "string"
}
```

### UserUpdate (全てオプショナル)

ユーザー更新時のリクエスト。

```json
{
  "email": "string (user@example.com)",
  "username": "string",
  "password": "string",
  "is_active": "boolean",
  "is_superuser": "boolean"
}
```

### UserResponse (UserBase を継承)

ユーザー情報のレスポンス。

```json
{
  "id": "integer",
  "email": "string (user@example.com)",
  "username": "string",
  "is_active": "boolean",
  "is_superuser": "boolean"
  // "created_at": "datetime", (例: "2024-07-30T10:00:00Z")
  // "updated_at": "datetime"
}
```

### ItemBase

アイテム情報の基本形。

```json
{
  "title": "string",
  "description": "string (nullable)"
}
```

### ItemCreate (ItemBase を継承)

アイテム作成時のリクエスト。

```json
{
  "title": "string",
  "description": "string (nullable)",
  "owner_id": "integer"
}
```

### ItemUpdate (ItemBase を継承、全てオプショナル)

アイテム更新時のリクエスト。

```json
{
  "title": "string",
  "description": "string (nullable)"
}
```

### ItemResponse (ItemBase を継承)

アイテム情報のレスポンス。

```json
{
  "id": "integer",
  "title": "string",
  "description": "string (nullable)",
  "owner_id": "integer"
}
```

## 認証 (Auth)

### ログイン

`POST /api/v1/auth/login`

ユーザー認証を行い、アクセストークンを取得します。

**リクエストボディ (application/x-www-form-urlencoded):**

- `username`: string (ユーザーのメールアドレスまたはユーザー名)
- `password`: string

**成功時のレスポンス (200 OK):** `Token`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**エラーレスポンス:**

- `401 Unauthorized`: 認証情報が不正な場合。

## ユーザー (Users)

### ユーザー一覧の取得

`GET /api/v1/users/`

ユーザーの一覧を取得します。
**認証**: 必要 (管理者権限が意図されていますが、現状の実装では強制されていません)

**クエリパラメータ:**

- `skip` (integer, optional, default: 0): スキップするアイテム数。
- `limit` (integer, optional, default: 100): 取得する最大アイテム数。

**成功時のレスポンス (200 OK):** `List[UserResponse]`

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "example_user",
    "is_active": true,
    "is_superuser": false
  }
]
```

### 新規ユーザー作成

`POST /api/v1/users/`

新しいユーザーを作成します。
**認証**: 不要 (ただし、本番環境では通常保護されます)

**リクエストボディ:** `UserCreate`

```json
{
  "email": "newuser@example.com",
  "username": "new_user",
  "password": "securepassword123"
}
```

**成功時のレスポンス (201 Created):** `UserResponse`

```json
{
  "id": 2,
  "email": "newuser@example.com",
  "username": "new_user",
  "is_active": true,
  "is_superuser": false
}
```

### 特定ユーザー情報の取得

`GET /api/v1/users/{user_id}`

指定されたIDのユーザー情報を取得します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**成功時のレスポンス (200 OK):** `UserResponse`

**エラーレスポンス:**

- `404 Not Found`: ユーザーが見つからない場合。

### ユーザー情報の更新

`PUT /api/v1/users/{user_id}`

指定されたIDのユーザー情報を更新します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**リクエストボディ:** `UserUpdate`

```json
{
  "username": "updated_user_name",
  "is_active": false
}
```

**成功時のレスポンス (200 OK):** `UserResponse`

**エラーレスポンス:**

- `404 Not Found`: ユーザーが見つからない場合。

### ユーザーの削除

`DELETE /api/v1/users/{user_id}`

指定されたIDのユーザーを削除します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**成功時のレスポンス (204 No Content)**

**エラーレスポンス:**

- `404 Not Found`: ユーザーが見つからない場合。


## アイテム (Items)

### アイテム一覧の取得

`GET /api/v1/items/`

アイテムの一覧を取得します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**クエリパラメータ:**

- `skip` (integer, optional, default: 0): スキップするアイテム数。
- `limit` (integer, optional, default: 100): 取得する最大アイテム数。

**成功時のレスポンス (200 OK):** `List[ItemResponse]`

```json
[
  {
    "id": 1,
    "title": "サンプルアイテム",
    "description": "これはサンプルアイテムです",
    "owner_id": 1
  }
]
```

### 新規アイテム作成

`POST /api/v1/items/`

新しいアイテムを作成します。
**認証**: 必要 (現状の実装では強制されていません)

**リクエストボディ:** `ItemCreate`

```json
{
  "title": "新しいアイテム",
  "description": "これは新しいアイテムです",
  "owner_id": 1
}
```

**成功時のレスポンス (201 Created):** `ItemResponse`

```json
{
  "id": 1,
  "title": "新しいアイテム",
  "description": "これは新しいアイテムです",
  "owner_id": 1
}
```

### 特定アイテム情報の取得

`GET /api/v1/items/{item_id}`

指定されたIDのアイテム情報を取得します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**成功時のレスポンス (200 OK):** `ItemResponse`

**エラーレスポンス:**

- `404 Not Found`: アイテムが見つからない場合。

### アイテム情報の更新

`PUT /api/v1/items/{item_id}`

指定されたIDのアイテム情報を更新します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**リクエストボディ:** `ItemUpdate`

```json
{
  "title": "更新されたアイテム名",
  "description": "更新された説明"
}
```

**成功時のレスポンス (200 OK):** `ItemResponse`

**エラーレスポンス:**

- `404 Not Found`: アイテムが見つからない場合。

### アイテムの削除

`DELETE /api/v1/items/{item_id}`

指定されたIDのアイテムを削除します。
**認証**: 必要性が高いエンドポイントです (現状の実装では強制されていません)

**成功時のレスポンス (204 No Content)**

**エラーレスポンス:**

- `404 Not Found`: アイテムが見つからない場合。


## エラーレスポンスの共通形式

一般的なエラーレスポンスは以下の形式です。

```json
{
  "detail": "エラーメッセージ"
}
```

### 主なHTTPステータスコード

- `200 OK`: リクエスト成功。
- `201 Created`: リソース作成成功。
- `204 No Content`: リソース削除成功などで、レスポンスボディなし。
- `400 Bad Request`: リクエストが無効な場合 (例: バリデーションエラー)。
- `401 Unauthorized`: 認証が必要だが提供されていない、または無効な場合。
- `403 Forbidden`: 認証済みだが、リソースへのアクセス権限がない場合。
- `404 Not Found`: 要求されたリソースが見つからない場合。
- `422 Unprocessable Entity`: リクエストは正しいが、意味的に処理できない場合（FastAPIのデフォルトバリデーションエラー）。

## レート制限 (参考情報)

- (もし設定されていれば) 認証済みユーザー: 1分あたりXXリクエスト
- (もし設定されていれば) 未認証ユーザー: 1分あたりYYリクエスト
*(注意: レート制限は現状のコードからは確認できません。インフラ側や別途ミドルウェアで設定される場合があります。)*
