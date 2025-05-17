"""APIルート定義モジュール

このモジュールでは、APIルートを一元管理します。
"""

from fastapi import APIRouter

from backend.api.endpoints import auth, items, users

# メインのAPIルーター
api_router = APIRouter()

# 認証関連のルート
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# ユーザー関連のルート
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# アイテム関連のルート
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"]
)
