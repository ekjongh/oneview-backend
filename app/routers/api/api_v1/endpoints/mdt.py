from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.mdt import get_mdt_trend_by_group_date2, \
    get_worst10_mdt_bts_by_group_date2,\
    get_mdt_trend_item_by_group_date


router = APIRouter()


@router.get("/trend-day2", response_model=List[schemas.MdtTrendOutput])
async def get_mdt_trend_day2(code:str=None, group:str="", start_date: str = "20220710", end_date: str = None, db: SessionLocal = Depends(get_db)):
    mdt_trend_days = await get_mdt_trend_by_group_date2(db=db, code=code, group=group, start_date=start_date, end_date=end_date)
    return mdt_trend_days


@router.get("/worst2", response_model=List[schemas.MdtBtsOutput])
async def get_worst_mdt_bts2(limit: int = 10, code:str=None, group:str="", start_date: str = "20220801", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_mdt_bts = await get_worst10_mdt_bts_by_group_date2(db=db, code=code, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_mdt_bts

@router.get("/trend-item-day", response_model=List[schemas.MdtTrendItemOutput])
async def get_mdt_trend_item_day(code:str=None, group:str="", start_date: str = "20220710", end_date: str = None, db: SessionLocal = Depends(get_db)):
    mdt_trend_days = await get_mdt_trend_item_by_group_date(db=db, code=code, group=group, start_date=start_date, end_date=end_date)
    return mdt_trend_days

