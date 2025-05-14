from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def get_item(db: Session, item_id: int) -> Optional[Item]:
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(
    db: Session, skip: int = 0, limit: int = 100, owner_id: Optional[int] = None
) -> List[Item]:
    query = db.query(Item)
    if owner_id is not None:
        query = query.filter(Item.owner_id == owner_id)
    return query.offset(skip).limit(limit).all()


def create_user_item(db: Session, item: ItemCreate, owner_id: int) -> Item:
    db_item = Item(**item.dict(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    update_data = item_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, db_item: Item) -> None:
    db.delete(db_item)
    db.commit()
