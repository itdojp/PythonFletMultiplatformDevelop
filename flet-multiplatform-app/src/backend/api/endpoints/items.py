"""アイテム関連のAPIエンドポイント"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import AsyncDbSession
from backend.models.item import Item
from backend.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter()


@router.get("/", response_model=List[ItemResponse])
async def read_items(
    db: AsyncDbSession,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """アイテム一覧を取得する"""
    # TODO: 実際のアイテム取得ロジックを実装
    items = await db.query(Item).offset(skip).limit(limit).all()
    return items


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    db: AsyncDbSession,
    item_in: ItemCreate,
) -> Any:
    """新しいアイテムを作成する"""
    # TODO: 実際のアイテム作成ロジックを実装
    item = Item(
        title=item_in.title,
        description=item_in.description,
        owner_id=item_in.owner_id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    db: AsyncDbSession,
) -> Any:
    """特定のアイテム情報を取得する"""
    # TODO: 実際のアイテム取得ロジックを実装
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="アイテムが見つかりません",
        )
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: AsyncDbSession,
) -> Any:
    """アイテム情報を更新する"""
    # TODO: 実際のアイテム更新ロジックを実装
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="アイテムが見つかりません",
        )

    update_data = item_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncDbSession,
) -> None:
    """アイテムを削除する"""
    # TODO: 実際のアイテム削除ロジックを実装
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="アイテムが見つかりません",
        )

    await db.delete(item)
    await db.commit()
