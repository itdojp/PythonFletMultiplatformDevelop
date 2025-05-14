"""APIの依存関係を提供するモジュール"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.deps import (
    get_current_active_superuser,
    get_current_active_user,
    get_current_user,
)
from config.database import get_db

# 依存関係のエイリアス
CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]
CurrentActiveSuperuser = Annotated[dict, Depends(get_current_active_superuser)]
AsyncDbSession = Annotated[AsyncSession, Depends(get_db)]


def get_async_db() -> AsyncSession:
    """非同期データベースセッションを取得する"""
    return get_db()
