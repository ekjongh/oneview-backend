from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.mdt import get_mdt_trend_by_group_date


router = APIRouter()


@router.get("/trend-day", response_model=List[schemas.MdtTrendOutput])
async def get_mdt_trend_day(group:str="", start_date: str = "20220710", end_date: str = None, db: SessionLocal = Depends(get_db)):
    mdt_trend_days = get_mdt_trend_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date)
    return mdt_trend_days