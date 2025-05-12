from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDBBase(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class Item(ItemInDBBase):
    pass

class ItemInDB(ItemInDBBase):
    pass
