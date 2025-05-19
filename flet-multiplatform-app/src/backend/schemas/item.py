"""アイテム関連のスキーマを定義するモジュール"""

from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """アイテムの基本スキーマ"""

    title: str = Field(..., description="アイテムのタイトル", max_length=100)
    description: Optional[str] = Field(None, description="アイテムの説明")


class ItemCreate(ItemBase):
    """アイテム作成スキーマ"""

    owner_id: int = Field(..., description="所有者のID")


class ItemUpdate(ItemBase):
    """アイテム更新スキーマ"""

    title: Optional[str] = Field(None, description="アイテムのタイトル", max_length=100)


class ItemResponse(ItemBase):
    """アイテムレスポンススキーマ"""

    id: int = Field(..., description="アイテムのID")
    owner_id: int = Field(..., description="所有者のID")

    class Config:
        """Pydantic設定クラス"""

        from_attributes = True
