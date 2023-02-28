from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.volte import get_worst10_volte_bts_by_group_date, \
        get_worst10_volte_hndset_by_group_date, \
        get_volte_trend_by_group_date, \
        get_volte_trend_item_by_group_date, \
        get_volte_trend_by_group_month, \
        get_volte_trend_item_by_group_month, \
        get_volte_compare_by_prod

router = APIRouter()

# 주기지국 Volte 기준 Worst TOP 10
@router.get("/worst", response_model=List[schemas.VolteBtsOutput])
async def get_worst_volte_bts(limit: int = 10, prod:str=None, code:str="팀별", group:str="구로엔지니어링부", band:str=None,
                              start_date: str = "20220825", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_bts = await get_worst10_volte_bts_by_group_date(db=db, prod=prod, code=code, group=group,band=band,
                                                          start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_bts

# 단말 Volte 기준 Worst TOP 10
@router.get("/worst-hndset", response_model=List[schemas.VolteHndsetOutput])
async def get_worst_volte_hndset(limit: int = 10, prod:str=None, code:str=None, group:str="",
                                 start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_volte_hndset = await get_worst10_volte_hndset_by_group_date(db=db, prod=prod, code=code, group=group,
                                                                start_date=start_date, end_date=end_date, limit=limit)
    return worst_volte_hndset

@router.get("/trend-day", response_model=List[schemas.VolteTrendOutput])
async def get_volte_trend_daily(prod:str=None, code:str=None, group:str="",
                                start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_days = await get_volte_trend_by_group_date(db=db, prod=prod, code=code, group=group,
                                                     start_date=start_date, end_date=end_date)
    return volte_trend_days


@router.get("/trend-item-day", response_model=List[schemas.VolteTrendItemOutput])
async def get_volte_trend_item_daily(prod:str=None, code:str=None, group:str="", by:str="code",
                                start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_days = await get_volte_trend_item_by_group_date(db=db, prod=prod, code=code, group=group,by=by,
                                                     start_date=start_date, end_date=end_date)
    return volte_trend_days



@router.get("/trend-month", response_model=List[schemas.VolteTrendOutput])
async def get_volte_trend_month(prod:str=None, code:str=None, group:str="",
                                start_month: str = "202101", end_month: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_months = await get_volte_trend_by_group_month(db=db, prod=prod, code=code, group=group,
                                                     start_month=start_month, end_month=end_month)
    return volte_trend_months


@router.get("/trend-item-month", response_model=List[schemas.VolteTrendItemOutput])
async def get_volte_trend_item_month(prod:str=None, code:str=None, group:str="", by:str="code",
                                start_month: str = "202209", end_month: str = None, db: SessionLocal = Depends(get_db)):
    volte_trend_months = await get_volte_trend_item_by_group_month(db=db, prod=prod, code=code, group=group,by=by,
                                                     start_month=start_month, end_month=end_month)
    return volte_trend_months


@router.get("/compare-prod", response_model=List[schemas.VolteCompareProdOutput])
async def get_volte_by_prod(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    list_compare = await get_volte_compare_by_prod(db=db, code=code, group=group, start_date=start_date)
    return list_compare