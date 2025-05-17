"""セキュリティ関連のユーティリティを提供するモジュール"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from backend.core.config import settings

# パスワードのハッシュ化に使用するコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証する

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        bool: パスワードが一致する場合はTrue
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化する

    Args:
        password: 平文パスワード

    Returns:
        str: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """アクセストークンを作成する

    Args:
        subject: トークンのサブジェクト（通常はユーザーID）
        expires_delta: トークンの有効期限（省略時は設定値を使用）

    Returns:
        str: 生成されたJWTトークン
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt
