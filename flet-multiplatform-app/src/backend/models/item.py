"""アイテムモデルを定義するモジュール"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.core.db import Base


class Item(Base):
    """アイテムモデル"""

    __tablename__ = "item"

    # 基本フィールド
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 基本情報
    title = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)

    # 所有者との関連付け
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="items")

    def __repr__(self) -> str:
        """文字列表現を返す"""
        return f"<Item {self.title}>"
