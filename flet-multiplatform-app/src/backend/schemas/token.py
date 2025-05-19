"""認証トークン関連のスキーマを定義するモジュール"""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """アクセストークンスキーマ"""

    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(..., description="トークンタイプ")


class TokenPayload(BaseModel):
    """トークンペイロードスキーマ"""

    sub: Optional[str] = Field(None, description="サブジェクト（通常はユーザーID）")
    exp: Optional[int] = Field(None, description="有効期限（UNIX時間）")
