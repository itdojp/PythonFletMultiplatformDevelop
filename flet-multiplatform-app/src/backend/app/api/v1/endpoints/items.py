from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.api import deps
from backend.app.services import item_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    items = item_service.get_items(db, skip=skip, limit=limit, owner_id=current_user.id)
    return items


@router.post("/", response_model=schemas.Item)
def create_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = item_service.create_user_item(db, item=item_in, owner_id=current_user.id)
    return item


@router.put("/{item_id}", response_model=schemas.Item)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = item_service.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = item_service.update_item(db, db_item=item, item_in=item_in)
    return item


@router.get("/{item_id}", response_model=schemas.Item)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = item_service.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{item_id}", response_model=schemas.Item)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = item_service.get_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item_service.delete_item(db, db_item=item)
    return item
