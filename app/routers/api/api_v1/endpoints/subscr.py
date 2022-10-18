from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.subscr import get_subscr_compare_by_hndset, get_subscr_compare_by_hndset2, get_subscr_compare_by_prod

router = APIRouter()


@router.get("/compare_hndset", response_model=List[schemas.SubscrCompareOutput])
async def get_subscr_by_hndset2(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    subscr_compare = await get_subscr_compare_by_hndset2(db=db, code=code, group=group, start_date=start_date)
    return subscr_compare

@router.get("/compare_prod", response_model=List[schemas.SubscrCompareProdOutput])
async def get_subscr_by_prod(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    subscr_compare = await get_subscr_compare_by_prod(db=db, code=code, group=group, start_date=start_date)
    return subscr_compare

#############################
@router.get("/compare", response_model=List[schemas.SubscrCompareOutput])
async def get_subscr_by_hndset(group:str="", start_date: str = "20220710", db: SessionLocal = Depends(get_db)):
    subscr_compare = await get_subscr_compare_by_hndset(db=db, group=group, start_date=start_date)
    return subscr_compare

