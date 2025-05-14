"""データベースモデルの基本クラスを定義するモジュール"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """すべてのモデルの基底クラス"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """テーブル名を自動的に生成する"""
        return cls.__name__.lower()

    # 共通カラム
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        """モデルを辞書に変換する"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
