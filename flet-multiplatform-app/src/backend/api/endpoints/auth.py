"""認証関連のAPIエンドポイント"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.deps import AsyncDbSession
from backend.core.config import settings
from backend.core.security import create_access_token, verify_password
from backend.models.user import User
from backend.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncDbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2互換のトークンログインエンドポイント。

    このエンドポイントは、ユーザー名（メールアドレス）とパスワードで認証し、
    アクセストークンを返します。
    """
    # TODO: 実際のユーザー認証ロジックを実装
    # これは仮の実装です
    user = await db.get(User, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="不正なユーザー名またはパスワードです",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
