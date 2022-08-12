from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.volte import get_volte_event_by_group_date, \
        get_volte_trend_by_group_date, \
        get_worst10_volte_bts_by_group_date, \
        get_worst10_volte_hndset_by_group_date

router = APIRouter()

# 주기지국 Volte 기준 Worst TOP 10
@router.get("/worst", response_model=List[schemas.VolteBtsOutput])
async def get_worst_volte_bts(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_bts = get_worst10_volte_bts_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_bts

# 단말 Volte 기준 Worst TOP 10
@router.get("/worst_hndset", response_model=List[schemas.VolteHndsetOutput])
async def get_worst_volte_hndset(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_hndset = get_worst10_volte_hndset_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_hndset

@router.get("/trend-day", response_model=List[schemas.VolteTrendOutput])
async def get_volte_trend_daily(group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_days = get_volte_trend_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date)
    return volte_trend_days



@router.get("/kpi-day", response_model=schemas.VolteEventOutput)
async def get_volte_event_day(group:str="", date:str="20220502", db: SessionLocal = Depends(get_db)):
    volte_event_days = get_volte_event_by_group_date(db=db, group=group, date=date)
    return volte_event_days

