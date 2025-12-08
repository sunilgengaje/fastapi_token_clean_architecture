# app/repositories/item_repository.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_for_user(self, owner_id: int, item_in: ItemCreate) -> Item:
        item = Item(
            title=item_in.title,
            description=item_in.description,
            owner_id=owner_id,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_for_user(self, owner_id: int) -> List[Item]:
        return self.db.query(Item).filter(Item.owner_id == owner_id).all()

    def get_by_id_and_owner(self, item_id: int, owner_id: int) -> Optional[Item]:
        return (
            self.db.query(Item)
            .filter(Item.id == item_id, Item.owner_id == owner_id)
            .first()
        )
