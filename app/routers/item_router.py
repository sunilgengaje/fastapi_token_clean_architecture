# app/routers/item_router.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.item import ItemCreate, ItemRead
from app.schemas.auth import UserRead
from app.services.item_service import ItemService
from app.services.auth_service import get_current_active_user

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item_route(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    service = ItemService(db=db)
    return service.create_item_for_user(item_in, current_user)


@router.get("/", response_model=List[ItemRead])
def list_items_route(
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    service = ItemService(db=db)
    return service.list_items_for_user(current_user)


@router.get("/{item_id}", response_model=ItemRead)
def get_item_route(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_active_user),
):
    service = ItemService(db=db)
    return service.get_item_for_user(item_id, current_user)
