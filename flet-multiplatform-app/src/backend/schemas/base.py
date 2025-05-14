"""スキーマの基本クラスを定義するモジュール"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """すべてのスキーマの基底クラス"""

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
        },
    )


class BaseResponseSchema(BaseSchema):
    """レスポンススキーマの基底クラス"""

    id: int = Field(..., description="ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")


class BaseCreateSchema(BaseSchema):
    """作成スキーマの基底クラス"""

    pass


class BaseUpdateSchema(BaseSchema):
    """更新スキーマの基底クラス"""

    pass


class BaseInDB(BaseSchema):
    """データベースモデルの基底スキーマ"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """設定"""

        from_attributes = True
