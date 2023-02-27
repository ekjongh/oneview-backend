from typing import List

from fastapi import APIRouter, Depends

from app import schemas
from app.crud.item import get_items
from app.db.session import SessionLocal
from app.routers.api.deps import get_db

router = APIRouter()


@router.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items
