"""ユーザー関連のエンドポイントを定義するモジュール"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_active_superuser, get_current_active_user
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserUpdate
from backend.utils.security import get_password_hash

# 絶対インポートを使用
from config.database import get_db

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """現在のユーザー情報を取得する"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """現在のユーザー情報を更新する"""
    # メールアドレスの重複チェック
    if user_in.email != current_user.email:
        user = await db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています",
            )
    # ユーザー名の重複チェック
    if user_in.username != current_user.username:
        user = await db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このユーザー名は既に使用されています",
            )
    # ユーザー情報の更新
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("", response_model=List[UserResponse])
async def read_users(
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """ユーザー一覧を取得する（管理者のみ）"""
    users = await db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("", response_model=UserResponse)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_in: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> User:
    """ユーザーを作成する（管理者のみ）"""
    # ユーザー名の重複チェック
    user = await db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に使用されています",
        )
    # メールアドレスの重複チェック
    user = await db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に使用されています",
        )
    # ユーザーの作成
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> User:
    """ユーザー情報を取得する（管理者のみ）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> User:
    """ユーザー情報を更新する（管理者のみ）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    # メールアドレスの重複チェック
    if user_in.email != user.email:
        existing_user = await db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています",
            )
    # ユーザー名の重複チェック
    if user_in.username != user.username:
        existing_user = (
            await db.query(User).filter(User.username == user_in.username).first()
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このユーザー名は既に使用されています",
            )
    # ユーザー情報の更新
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> User:
    """ユーザーを削除する（管理者のみ）"""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    await db.delete(user)
    await db.commit()
    return user
