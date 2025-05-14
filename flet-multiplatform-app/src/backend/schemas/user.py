"""ユーザースキーマを定義するモジュール"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr

from .base import BaseCreateSchema, BaseResponseSchema, BaseUpdateSchema


class UserBase(BaseModel):
    """ユーザーの基本スキーマ"""

    email: EmailStr = Field(..., description="メールアドレス")
    username: constr(min_length=3, max_length=50) = Field(..., description="ユーザー名")
    full_name: Optional[str] = Field(None, description="氏名")


class UserCreate(UserBase, BaseCreateSchema):
    """ユーザー作成スキーマ"""

    password: constr(min_length=8) = Field(..., description="パスワード")


class UserUpdate(UserBase, BaseUpdateSchema):
    """ユーザー更新スキーマ"""

    password: Optional[constr(min_length=8)] = Field(None, description="パスワード")
    is_active: Optional[bool] = Field(None, description="アクティブ状態")
    is_superuser: Optional[bool] = Field(None, description="管理者権限")


class UserInDB(UserBase, BaseResponseSchema):
    """データベース内のユーザースキーマ"""

    is_active: bool = Field(..., description="アクティブ状態")
    is_superuser: bool = Field(..., description="管理者権限")
    last_login: Optional[datetime] = Field(None, description="最終ログイン日時")


class UserResponse(UserInDB):
    """ユーザーレスポンススキーマ"""

    pass


class Token(BaseModel):
    """トークンスキーマ"""

    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field("bearer", description="トークンタイプ")


class TokenPayload(BaseModel):
    """トークンペイロードスキーマ"""

    sub: Optional[int] = None
    exp: Optional[datetime] = None
