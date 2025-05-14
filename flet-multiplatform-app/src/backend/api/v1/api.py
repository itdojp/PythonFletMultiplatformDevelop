"""APIルーターを定義するモジュール"""

from fastapi import APIRouter

from .endpoints import auth, users

api_router = APIRouter()

# 認証関連のエンドポイント
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["認証"],
)

# ユーザー関連のエンドポイント
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["ユーザー"],
) 