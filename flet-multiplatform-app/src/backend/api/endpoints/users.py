"""ユーザー関連のAPIエンドポイント"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import AsyncDbSession
from backend.core.security import get_password_hash
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: AsyncDbSession,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """ユーザー一覧を取得する"""
    # TODO: 実際のユーザー取得ロジックを実装
    users = await db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    db: AsyncDbSession,
    user_in: UserCreate,
) -> Any:
    """新しいユーザーを作成する"""
    # TODO: 実際のユーザー作成ロジックを実装
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncDbSession,
) -> Any:
    """特定のユーザー情報を取得する"""
    # TODO: 実際のユーザー取得ロジックを実装
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncDbSession,
) -> Any:
    """ユーザー情報を更新する"""
    # TODO: 実際のユーザー更新ロジックを実装
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncDbSession,
) -> None:
    """ユーザーを削除する"""
    # TODO: 実際のユーザー削除ロジックを実装
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    await db.delete(user)
    await db.commit()
