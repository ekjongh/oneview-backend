from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.data_cnt import get_datacnt_compare_by_prod, \
    get_datacnt_trend_by_group_date,\
    get_datacnt_trend_item_by_group_date

router = APIRouter()

@router.get("/compare-prod", response_model=List[schemas.DataCntCompareProdOutput])
async def get_datacnt_by_prod(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    datacnt_compare = await get_datacnt_compare_by_prod(db=db, code=code, group=group, start_date=start_date)
    return datacnt_compare


@router.get("/trend-day", response_model=List[schemas.DataCntTrendOutput])
async def get_datacnt_trend_day(prod:str=None, code:str=None, group:str="",
                                 start_date: str = "20220905", end_date: str=None, db: SessionLocal = Depends(get_db)):
    datacnt_trend_days = await get_datacnt_trend_by_group_date(db=db, prod=prod, code=code, group=group,
                                                                start_date=start_date, end_date=end_date)
    return datacnt_trend_days

@router.get("/trend-item-day", response_model=List[schemas.DataCntTrendItemOutput])
async def get_datacnt_trend_item_daily(prod:str=None, code:str=None, group:str="", by:str="code",
                                start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    datacnt_trend_days = await get_datacnt_trend_item_by_group_date(db=db, prod=prod, code=code, group=group,by=by,
                                                     start_date=start_date, end_date=end_date)
    return datacnt_trend_days
