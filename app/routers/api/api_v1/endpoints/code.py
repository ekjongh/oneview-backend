from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.code import get_addr_code_all, get_org_code_all, get_menu_code_all

router = APIRouter()


@router.get("/addr", response_model=List[schemas.AddrCodeOutput])
async def get_addr_code(sido:str=None, gungu:str=None, dong:str=None, db: SessionLocal = Depends(get_db)):
    return await get_addr_code_all(sido=sido, gungu=gungu, dong=dong, db=db)


@router.get("/org", response_model=List[schemas.OrgCodeOutput])
async def get_org_code(db: SessionLocal = Depends(get_db)):
    return await get_org_code_all(db=db)


@router.get("/menu", response_model=List[schemas.MenuCodeOutput])
async def get_menu_code(db: SessionLocal = Depends(get_db)):
    return await get_menu_code_all(db=db)


@router.get("/cmpn")
async def get_maker_code():
    maker_list = ["삼성전자", "노키아", "에릭슨엘지(주)", "이노와이어리스", "(주)주니코리아"]
    return maker_list
