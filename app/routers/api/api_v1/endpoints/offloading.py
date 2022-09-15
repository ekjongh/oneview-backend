from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.offloading import get_offloading_trend_by_group_date, get_worst10_offloading_jo_by_group_date, \
    get_offloading_event_by_group_date, \
    get_worst10_offloading_hndset_by_group_date, \
    get_worst10_offloading_dong_by_group_date, \
    get_worst10_offloading_jo_by_group_date2, \
    get_worst10_offloading_hndset_by_group_date2, \
    get_offloading_trend_by_group_date2, \
    get_offloading_trend_item_by_group_date

router = APIRouter()

@router.get("/worst2", response_model=List[schemas.OffloadingBtsOutput])
async def get_worst_offloading_bts2(limit: int = 10, code:str=None, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_offloading_bts = get_worst10_offloading_jo_by_group_date2(db=db, code=code, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_offloading_bts

@router.get("/worst_hndset2", response_model=List[schemas.OffloadingHndsetOutput])
async def get_worst_offloading_hndset2(limit: int = 10, code:str=None, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_offloading_hndset = get_worst10_offloading_hndset_by_group_date2(db=db, code=code, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_offloading_hndset

@router.get("/trend-day2", response_model=List[schemas.OffloadingTrendOutput])
async def get_offloading_trend_day2(code:str=None, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    offloading_trend_days = get_offloading_trend_by_group_date2(db=db, code=code, group=group, start_date=start_date, end_date=end_date)
    return offloading_trend_days

@router.get("/kpi-day", response_model=schemas.OffloadingEventOutput)
async def get_offloading_kpi_day(group:str="", date:str="20220502", db: SessionLocal = Depends(get_db)):
    offloading_event_days = get_offloading_event_by_group_date(db=db, group=group, date=date)
    return offloading_event_days

@router.get("/worst_dong", response_model=List[schemas.OffloadingDongOutput])
async def get_worst_offloading_dong(limit: int = 10, code:str=None, group:str="", start_date: str = "20220821", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_offloading_dong = get_worst10_offloading_dong_by_group_date(db=db, code=code, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_offloading_dong

@router.get("/trend-item-day", response_model=List[schemas.OffloadingTrendItemOutput])
async def get_offloading_trend_item_daily(code:str=None, group:str="",
                                start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    offloading_trend_days = get_offloading_trend_item_by_group_date(db=db, code=code, group=group,
                                                     start_date=start_date, end_date=end_date)
    return offloading_trend_days

############################
@router.get("/worst", response_model=List[schemas.OffloadingBtsOutput])
async def get_worst_offloading_bts(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_offloading_bts = get_worst10_offloading_jo_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_offloading_bts

@router.get("/worst_hndset", response_model=List[schemas.OffloadingHndsetOutput])
async def get_worst_offloading_hndset(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_offloading_hndset = get_worst10_offloading_hndset_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_offloading_hndset

@router.get("/trend-day", response_model=List[schemas.OffloadingTrendOutput])
async def get_offloading_trend_day(group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    offloading_trend_days = get_offloading_trend_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date)
    return offloading_trend_days

