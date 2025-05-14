"""データベースの初期化スクリプト"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ...config.database import AsyncSessionLocal
from ...config.logging import get_logger
from ..models import User
from ..schemas import UserCreate
from ..utils.security import get_password_hash

logger = get_logger(__name__)


async def init_db() -> None:
    """データベースを初期化する"""
    async with AsyncSessionLocal() as db:
        await create_first_superuser(db)


async def create_first_superuser(db: AsyncSession) -> None:
    """最初の管理者ユーザーを作成する"""
    # 管理者ユーザーの存在確認
    superuser = await db.query(User).filter(User.is_superuser == True).first()
    if superuser:
        logger.info("管理者ユーザーは既に存在します")
        return

    # 管理者ユーザーの作成
    superuser_in = UserCreate(
        email="admin@example.com",
        username="admin",
        password="admin",  # 本番環境では必ず変更してください
        full_name="Administrator",
    )
    superuser = User(
        email=superuser_in.email,
        username=superuser_in.username,
        hashed_password=get_password_hash(superuser_in.password),
        full_name=superuser_in.full_name,
        is_active=True,
        is_superuser=True,
        last_login=datetime.utcnow(),
    )
    db.add(superuser)
    await db.commit()
    logger.info("管理者ユーザーを作成しました")


if __name__ == "__main__":
    asyncio.run(init_db())
