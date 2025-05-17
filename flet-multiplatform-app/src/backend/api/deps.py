"""APIの依存関係を提供するモジュール"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.db import get_db
from backend.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

# 依存関係のエイリアス
# 注: 認証関連の依存関係は再実装します
# CurrentUser = Annotated[dict, Depends(get_current_user)]
# CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]
# CurrentActiveSuperuser = Annotated[dict, Depends(get_current_active_superuser)]

# DBセッション依存関係
AsyncDbSession = Annotated[AsyncSession, Depends(get_db)]


def get_async_db() -> AsyncSession:
    """非同期データベースセッションを取得する"""
    return get_db()
