from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.subscr import get_subscr_compare_by_hndset, \
                            get_subscr_compare_by_prod, \
                            get_subscr_trend_by_group_date, \
                            get_subscr_trend_item_by_group_date, \
                            get_subscr_trend_by_group_month, \
                            get_subscr_trend_item_by_group_month

router = APIRouter()


@router.get("/compare-hndset", response_model=List[schemas.SubscrCompareOutput])
async def get_subscr_by_hndset(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    subscr_compare = await get_subscr_compare_by_hndset(db=db, code=code, group=group, start_date=start_date)
    return subscr_compare

@router.get("/compare-prod", response_model=List[schemas.SubscrCompareProdOutput])
async def get_subscr_by_prod(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    subscr_compare = await get_subscr_compare_by_prod(db=db, code=code, group=group, start_date=start_date)
    return subscr_compare


@router.get("/trend-day", response_model=List[schemas.SubscrTrendOutput])
async def get_sbscr_trend_daily(prod:str=None, code:str=None, group:str="",
                                start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    subscr_trend_days = await get_subscr_trend_by_group_date(db=db, prod=prod, code=code, group=group,
                                                     start_date=start_date, end_date=end_date)
    return subscr_trend_days


@router.get("/trend-item-day", response_model=List[schemas.SubscrTrendItemOutput])
async def get_subscr_trend_item_daily(prod:str=None, code:str=None, group:str="", by:str="code",
                                start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    subscr_trend_days = await get_subscr_trend_item_by_group_date(db=db, prod=prod, code=code, group=group, by=by,
                                                     start_date=start_date, end_date=end_date)
    return subscr_trend_days



@router.get("/trend-month", response_model=List[schemas.SubscrTrendOutput])
async def get_subscr_trend_month(prod:str=None, code:str=None, group:str="",
                                start_month: str = "202101", end_month: str = None, db: SessionLocal = Depends(get_db)):
    subscr_trend_months = await get_subscr_trend_by_group_month(db=db, prod=prod, code=code, group=group,
                                                     start_month=start_month, end_month=end_month)
    return subscr_trend_months


@router.get("/trend-item-month", response_model=List[schemas.SubscrTrendItemOutput])
async def get_subscr_trend_item_month(prod:str=None, code:str=None, group:str="", by:str="code",
                                start_month: str = "202201", end_month: str = None, db: SessionLocal = Depends(get_db)):
    subscr_trend_months = await get_subscr_trend_item_by_group_month(db=db, prod=prod, code=code, group=group, by=by,
                                                     start_month=start_month, end_month=end_month)
    return subscr_trend_months
