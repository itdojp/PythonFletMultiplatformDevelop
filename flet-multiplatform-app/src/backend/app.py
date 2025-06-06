"""FastAPIアプリケーションを定義するモジュール"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import api_router
from backend.core.config import settings

# ロギング設定はコアモジュールで対応
# 必要に応じてロギング設定を行う

# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORSミドルウェアの設定
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# APIルーターの追加
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Welcome to Flet Multiplatform App API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}
