from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.volte import get_worst10_volte_bts_by_group_date2, \
        get_worst10_volte_hndset_by_group_date2, \
        get_volte_trend_by_group_date2, \
        get_volte_trend_item_by_group_date

router = APIRouter()

# 주기지국 Volte 기준 Worst TOP 10
@router.get("/worst2", response_model=List[schemas.VolteBtsOutput])
async def get_worst_volte_bts2(limit: int = 10, prod:str=None, code:str="팀", group:str="구로엔지니어링부",
                              start_date: str = "20220825", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_bts = await get_worst10_volte_bts_by_group_date2(db=db, prod=prod, code=code, group=group,
                                                          start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_bts

# 단말 Volte 기준 Worst TOP 10
@router.get("/worst_hndset2", response_model=List[schemas.VolteHndsetOutput])
async def get_worst_volte_hndset2(limit: int = 10, prod:str=None, code:str=None, group:str="",
                                 start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_hndset = await get_worst10_volte_hndset_by_group_date2(db=db, prod=prod, code=code, group=group,
                                                                start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_hndset

@router.get("/trend-day2", response_model=List[schemas.VolteTrendOutput])
async def get_volte_trend_daily2(prod:str=None, code:str=None, group:str="",
                                start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_days = await get_volte_trend_by_group_date2(db=db, prod=prod, code=code, group=group,
                                                     start_date=start_date, end_date=end_date)
    return volte_trend_days



@router.get("/kpi-day", response_model=schemas.VolteEventOutput)
async def get_volte_event_day(prod:str=None, code:str=None, group:str="", date:str="20220502", db: SessionLocal = Depends(get_db)):
    volte_event_days = await get_volte_event_by_group_date(db=db, group=group, date=date)
    return volte_event_days

@router.get("/trend-item-day", response_model=List[schemas.VolteTrendItemOutput])
async def get_volte_trend_item_daily(prod:str=None, code:str=None, group:str="",
                                start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_days = await get_volte_trend_item_by_group_date(db=db, prod=prod, code=code, group=group,
                                                     start_date=start_date, end_date=end_date)
    return volte_trend_days

