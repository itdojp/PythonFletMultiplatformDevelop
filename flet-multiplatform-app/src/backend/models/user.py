"""ユーザーモデルを定義するモジュール"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.core.db import Base


class User(Base):
    """ユーザーモデル"""

    __tablename__ = "user"

    # 基本フィールド
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ユーザー情報
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # アカウント状態
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 認証関連
    last_login = Column(DateTime, nullable=True)

    # リレーションシップ
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """文字列表現を返す"""
        return f"<User {self.username}>"
