"""
アプリケーションのエントリーポイント
"""
import uvicorn

from .app import app
from .config import settings

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
