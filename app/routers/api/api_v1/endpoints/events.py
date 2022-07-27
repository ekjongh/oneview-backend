from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db

router = APIRouter()

@router.get("/bts")
async def get_all_bts_events(db: SessionLocal = Depends(get_db)):
    pass

@router.get("/bts/{id}")
async def get_bts_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.post("/bts/{id}")
async def register_bts_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.put("/bts/{id}")
async def update_bts_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.delete("/bts/{id}")
async def revoke_bts_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.get("/voc")
async def get_all_voc_events(db: SessionLocal = Depends(get_db)):
    pass

@router.get("/voc/{id}")
async def get_voc_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.post("/voc/{id}")
async def register_voc_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.put("/voc/{id}")
async def update_voc_event_by_id(db: SessionLocal = Depends(get_db)):
    pass

@router.delete("/voc/{id}")
async def revoke_voc_event_by_id(db: SessionLocal = Depends(get_db)):
    pass