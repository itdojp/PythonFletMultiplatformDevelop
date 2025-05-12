from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class CustomBase:
    # テーブル名を自動生成（クラス名をスネークケースに変換）
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # 共通のカラムをここに定義
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ベースモデルを作成
Base = CustomBase
