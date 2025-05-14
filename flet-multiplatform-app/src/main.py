"""メインアプリケーションファイル"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager

from .backend.app import app
from .backend.models import Base
from .config import settings
from .config.database import engine


@asynccontextmanager
async def lifespan(app):
    """アプリケーションのライフサイクルを管理する"""
    # 起動時の処理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # シャットダウン時の処理
    await engine.dispose()


# ライフサイクルイベントの設定
app.router.lifespan_context = lifespan


def main():
    """メイン関数"""
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()