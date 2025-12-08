# app/services/item_service.py
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemRead
from app.schemas.auth import UserRead


class ItemService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.item_repo = ItemRepository(self.db)

    def create_item_for_user(self, item_in: ItemCreate, user: UserRead) -> ItemRead:
        item = self.item_repo.create_for_user(owner_id=user.id, item_in=item_in)
        return ItemRead.model_validate(item)

    def list_items_for_user(self, user: UserRead) -> List[ItemRead]:
        items = self.item_repo.list_for_user(owner_id=user.id)
        return [ItemRead.model_validate(i) for i in items]

    def get_item_for_user(self, item_id: int, user: UserRead) -> ItemRead:
        item = self.item_repo.get_by_id_and_owner(item_id=item_id, owner_id=user.id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )
        return ItemRead.model_validate(item)
