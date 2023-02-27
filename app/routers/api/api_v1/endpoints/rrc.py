from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.rrc import get_rrc_trend_by_group_date,\
                        get_worst10_rrc_bts_by_group_date,\
                        get_rrc_trend_item_by_group_date, \
                        get_rrc_trend_item_by_group_month, \
                        get_rrc_trend_by_group_month


router = APIRouter()


@router.get("/trend-day", response_model=List[schemas.RrcTrendOutput])
async def get_rrc_trend_day(code:str=None, group:str="", start_date: str = "20220810", end_date: str = None, db: SessionLocal = Depends(get_db)):
    rrc_trend_days = await get_rrc_trend_by_group_date(db=db, code=code, group=group, start_date=start_date, end_date=end_date)
    return rrc_trend_days


@router.get("/worst", response_model=List[schemas.RrcBtsOutput])
async def get_worst_rrc_bts(limit: int = 10, code:str=None, group:str="", prod:str="RRC성공율", band:str=None,
                        start_date: str = "20220821", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_rrc_bts = await get_worst10_rrc_bts_by_group_date(db=db, code=code, group=group, prod=prod, band=band,
                        start_date=start_date, end_date=end_date, limit=limit)
    return worst_rrc_bts


@router.get("/trend-item-day", response_model=List[schemas.RrcTrendItemOutput])
async def get_rrc_trend_item_day(code:str=None, group:str="", start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    rrc_trend_days = await get_rrc_trend_item_by_group_date(db=db, code=code, group=group, start_date=start_date, end_date=end_date)
    return rrc_trend_days



@router.get("/trend-month", response_model=List[schemas.RrcTrendOutput])
async def get_rrc_trend_month(code:str=None, group:str="", start_month: str = "202101", end_month: str = None, db: SessionLocal = Depends(get_db)):
    rrc_trend_months = await get_rrc_trend_by_group_month(db=db, code=code, group=group, start_month=start_month, end_month=end_month)
    return rrc_trend_months



@router.get("/trend-item-month", response_model=List[schemas.RrcTrendItemOutput])
async def get_rrc_trend_item_month(code:str=None, group:str="", start_month: str = "202101",
                                   end_month: str = None, db: SessionLocal = Depends(get_db)):
    rrc_trend_months = await get_rrc_trend_item_by_group_month(db=db, code=code, group=group,
                                                            start_month=start_month, end_month=end_month)
    return rrc_trend_months