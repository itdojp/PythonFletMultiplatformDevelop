"""メインアプリケーションファイル"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent.parent))

# 絶対インポートを使用
from config import settings
from config.database import engine

# ロギングの設定
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)

# アプリケーションの作成
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# データベース接続の初期化
async def init_db():
    """データベースの初期化"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# アプリケーションのライフサイクル管理
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクルを管理する"""
    # 起動時の処理
    logger.info("Starting application...")

    # データベースの初期化
    await init_db()

    yield

    # シャットダウン時の処理
    logger.info("Shutting down application...")
    await engine.dispose()


# ライフサイクルイベントの設定
app.router.lifespan_context = lifespan


# ルートエンドポイント
@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    }


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok"}


def main():
    """メイン関数"""
    # ログ設定を適用
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_config["formats"]["access"] = settings.LOG_FORMAT
    uvicorn_log_config["formats"]["default"] = settings.LOG_FORMAT

    # アプリケーションの起動
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=uvicorn_log_config,
    )


if __name__ == "__main__":
    main()
