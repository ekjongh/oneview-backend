from typing import List

from app.errors import exceptions as ex
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.crud.dashboard_config import db_insert_dashboard_config_by_id,\
    db_get_dashboard_configs_by_userid, \
    db_get_dashboard_config_by_id, \
    db_update_dashboard_config_by_id, \
    db_delete_dashboard_config_by_id,\
    db_count_dashboard_config_by_id,\
    db_is_my_config_by_id
from app.routers.api.deps import get_db, get_current_user, get_current_active_user, get_db_sync
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOutput
from app.schemas.dashboard_config import DashboardConfigIn, DashboardConfigOut,  DashboardConfigList
# from app.utils.internel.user import dashboard_model_to_schema

from fastapi.responses import RedirectResponse

router = APIRouter()


# # ------------------------------- User DashBoard Config ... -------------------------------------- #
#
#
# @router.get("/boardconfig/all")
# async def read_dashboard_all_configs(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
#     """
#     사용자 대시보드 설정 전체 가져오기(관리자 페이지용)
#     :param skip:
#     :param limit:
#     :return: List(board_config)
#     """
#     board_configs = get_dashboard_configs(db=db, skip=skip, limit=limit)
#     result = [dashboard_model_to_schema(board_config) for board_config in board_configs]
#     return result
#
#
@router.get("/boardconfigs/me", response_model=List[DashboardConfigList])
def read_dashboard_config_by_userid(user: UserBase = Depends(get_current_user), db: SessionLocal = Depends(get_db_sync)):
    """
    내가 선택할 수 있는 대시보드 컨피그 목록 조회
    """
    return db_get_dashboard_configs_by_userid(db, user_id=user.user_id)

@router.get("/boardconfigs/{user_id}", response_model=List[DashboardConfigList])
def read_dashboard_config_by_userid(user_id: str, db: SessionLocal = Depends(get_db_sync)):
    """
    user_id가 선택할 수 있는 대시보드 컨피그 목록 조회
    """
    return db_get_dashboard_configs_by_userid(db, user_id=user_id)


@router.get("/boardconfig/{board_id}", response_model=DashboardConfigOut)
def read_dashboard_config_by_id(board_id: str, db: SessionLocal = Depends(get_db_sync), user: UserBase = Depends(get_current_user)):
# def read_dashboard_config_by_id(board_id: int, db: SessionLocal = Depends(get_db_sync)):
    """
    내가 선택한 대시보드 컨피그 상세 조회
    """
    board_config = db_get_dashboard_config_by_id(db, board_id=board_id, user_id=user.user_id)
    # board_config = db_get_dashboard_config_by_id(db, board_id=board_id, user_id="10077209")
    if board_config is None:
        raise HTTPException(status_code=404, detail="config not found")

    # group_3 = user.group_3
    # result.board_module = result.board_module.format(g_txt=user.group_3, c_txt="팀별")

    return board_config


@router.post("/boardconfig/{user_id}")
def create_dashboard_config_by_id(user_id: str, board_config: DashboardConfigIn, db: SessionLocal = Depends(get_db_sync)):
    """
    새로운 이름의 나의 대시보드 컨피그 생성 ( 나의 컨피그 5개가 넘을 시, 생성 불가 )
    """
    cnt = db_count_dashboard_config_by_id(user_id=user_id, db=db)
    if cnt >= 5:
        return {"result": "ERROR! 개인 Config는 최대 5개입니다.", "data": None}
    else:
        data = db_insert_dashboard_config_by_id(user_id=user_id, db=db, board_config=board_config)
        return {"result": "create Success!", "data": data}


@router.put("/boardconfig/{board_id}")
def update_dashboard_config_by_id(board_id: str, board_config: DashboardConfigIn, db: SessionLocal = Depends(get_db_sync)):
    """
    선택한 board_id에 대한 대시보드 컨피그 수정
    """
    data = db_update_dashboard_config_by_id(board_id=board_id, db=db, board_config=board_config)

    return {"result": "Update Success!", "data": data}


@router.delete("/boardconfig/{board_id}")
def delete_dashboard_config_by_id(board_id: int, db: SessionLocal = Depends(get_db_sync),
                                            user: UserBase = Depends(get_current_user)):
    """
    선택한 board_id에 대한 dashboard config 삭제 ( config 한개 남았을 시, 삭제 불가)
    """
    cnt = db_count_dashboard_config_by_id(user_id=user.user_id, db=db)
    if cnt<= 1:
        return {"result": "ERROR! 최소 1개의 Config가 필요합니다."}
    elif db_is_my_config_by_id(db=db, board_id=board_id):
        return {"result": "ERROR! my_config는 삭제 불가"}
    else :
        data = db_delete_dashboard_config_by_id(board_id=board_id, db=db)
        return {"result": "Delete Success!", "data": data}
