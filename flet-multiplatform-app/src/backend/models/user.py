"""ユーザーモデルを定義するモジュール"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """ユーザーモデル"""

    # ユーザー情報
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # アカウント状態
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # 認証関連
    last_login: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )

    def __repr__(self) -> str:
        """文字列表現を返す"""
        return f"<User {self.username}>" 