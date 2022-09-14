from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.data_cnt import get_datacnt_compare_by_prod

router = APIRouter()

@router.get("/compare_prod", response_model=List[schemas.DataCntCompareProdOutput])
async def get_datacnt_by_prod(code:str=None, group:str="", start_date: str = "20220905", db: SessionLocal = Depends(get_db)):
    datacnt_compare = get_datacnt_compare_by_prod(db=db, code=code, group=group, start_date=start_date)
    return datacnt_compare

