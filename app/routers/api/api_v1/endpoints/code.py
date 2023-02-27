########################################################################################################################
# 라우팅 테이블 - 공통서비스
#
# [ 서비스 리스트 ]
#  * 주소 : /addr
#  * 조직 : /org
#  * 메뉴 : /menu
#  * 제조사(협력사) : /cmpn
#  * 서비스 : /svcs
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.16 - 주석추가
#              기준일자 시점 데이터가 갱신된 테이블에 연관된 서비스 리스트 조회 서비스 추가
#
########################################################################################################################
from typing import List, Tuple

from fastapi import APIRouter, Depends
from datetime import datetime

from app.errors import exceptions as ex
from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.code import \
    get_addr_code_all, \
    get_org_code_center, \
    get_org_code_all, \
    get_menu_code_all,\
    get_svcs_list
from app.routers.api.deps import get_current_active_user

router = APIRouter()


@router.get("/addr", response_model=List[schemas.AddrCodeOutput])
async def get_addr_code(sido:str=None, gungu:str=None, dong:str=None, db: SessionLocal = Depends(get_db)):
    return await get_addr_code_all(sido=sido, gungu=gungu, dong=dong, db=db)


@router.get("/org")
async def get_org_code(bonbu:str=None, db: SessionLocal = Depends(get_db)):
    if not bonbu:
        return await get_org_code_center(db=db)
    else:
        return await get_org_code_all(db=db)

@router.get("/menu", response_model=List[schemas.MenuCodeOutput])
async def get_menu_code(db: SessionLocal = Depends(get_db)):
    return await get_menu_code_all(db=db)


@router.get("/cmpn")
async def get_maker_code():
    maker_list = ["삼성전자", "노키아", "에릭슨엘지(주)", "이노와이어리스", "(주)주니코리아"]
    return maker_list

# ======================================================================================================================
# 데이터가 갱신된 테이블에 관련된 서비스들을 조회하는 함수
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.16 - 초기모듈 작성
# ======================================================================================================================
@router.get("/svcs")
async def get_svcs(base_date:str=datetime.now().strftime("%Y%m%d"), db: SessionLocal = Depends(get_db)):
    """ 데이터가 갱신된 테이블에 관련된 서비스들을 조회하는 함수
        [ 파라미터 ]
         - 기준일자 : 문자열 (예: 20230209)
    """
    return await get_svcs_list(db=db, base_date=base_date)
