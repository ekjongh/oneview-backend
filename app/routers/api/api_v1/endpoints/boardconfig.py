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
    db_count_dashboard_config_by_id, \
    db_get_dashboard_default_config_by_id,\
    db_is_my_config_by_id, \
    db_get_dashboard_default_configs_by_user, \
    db_get_dashboard_configs
from app.routers.api.deps import get_db, get_current_user, get_current_active_user, get_db_sync
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOutput
from app.schemas.dashboard_config import DashboardConfigIn, DashboardConfigOut,  DashboardConfigList
from app.utils.internel.user import boardconfig_schema_to_model


router = APIRouter()


# # ------------------------------- User DashBoard Config ... -------------------------------------- #
#
#
@router.get("/boardconfig/all")
def read_dashboard_all_configs(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db_sync), client=Depends(get_current_active_user)):
    """
    사용자 대시보드 설정 전체 가져오기(관리자 페이지용)
    :param skip:
    :param limit:
    :return: List(board_config)
    """
    if not client.is_superuser:
        raise ex.NotAuthorized

    board_configs = db_get_dashboard_configs(db=db, skip=skip, limit=limit)
    # result = [dashboard_model_to_schema(board_config) for board_config in board_configs]
    print(board_configs)
    return board_configs


@router.get("/boardconfigs/me", response_model=List[DashboardConfigList])
def read_dashboard_config_by_userid(user: UserBase = Depends(get_current_active_user), db: SessionLocal = Depends(get_db_sync)):
    """
    내가 선택할 수 있는 대시보드 컨피그 목록 조회
    """
    result_list = []
    result_list.extend(db_get_dashboard_configs_by_userid(db, user_id=user.user_id))
    result_list.extend(db_get_dashboard_default_configs_by_user(db,user=user))

    return result_list


@router.get("/boardconfigs/{user_id}", response_model=List[DashboardConfigList])
def read_dashboard_config_by_userid(user_id: str, db: SessionLocal = Depends(get_db_sync), client=Depends(get_current_active_user)):
    """
    user_id가 선택할 수 있는 대시보드 컨피그 목록 조회
    """
    if not client.is_superuser:
        if client.user_id != user_id:
            raise ex.NotAuthorized

    return db_get_dashboard_configs_by_userid(db, user_id=user_id)


@router.get("/boardconfig/{board_id}", response_model=DashboardConfigOut)
def read_dashboard_config_by_id(board_id: int, db: SessionLocal = Depends(get_db_sync), client: UserBase = Depends(get_current_active_user)):
    """
    내가 선택한 대시보드 컨피그 상세 조회
    """
    if board_id > 10 :
        board_config = db_get_dashboard_config_by_id(db, board_id=board_id)
    else:
        board_config = db_get_dashboard_default_config_by_id(db=db, board_id=board_id, client=client)


    return board_config



@router.post("/boardconfig/{user_id}")
def create_dashboard_config_by_id(user_id: str, board_config: DashboardConfigIn, db: SessionLocal = Depends(get_db_sync)):
    """
    새로운 이름의 나의 대시보드 컨피그 생성 ( 나의 컨피그 5개가 넘을 시, 생성 불가 )
    """
    cnt = db_count_dashboard_config_by_id(user_id=user_id, db=db)
    if cnt > 5:
        return {"result": "ERROR! 개인 Config 개수 초과", "data": None}
    else:
        data = db_insert_dashboard_config_by_id(user_id=user_id, db=db, board_config=board_config)
        return {"result": "create Success!", "data": data}


@router.put("/boardconfig/{board_id}")
def update_dashboard_config_by_id(board_id: str, board_config: DashboardConfigIn, db: SessionLocal = Depends(get_db_sync), client: UserBase = Depends(get_current_user)):
    """
    선택한 board_id에 대한 대시보드 컨피그 수정
    """
    print("UPD", board_id, board_config)
    db_board_config = db_get_dashboard_config_by_id(db, board_id=board_id)

    if not client.is_superuser:
        if client.user_id != db_board_config.owner_id:
            # raise ex.NotAuthorized
            return {"result":"not allowed"}

    data = db_update_dashboard_config_by_id(board_id=board_id, db=db, board_config=board_config)

    return {"result": "Update Success!", "data": data}



@router.delete("/boardconfig/{board_id}")
def delete_dashboard_config_by_id(board_id: int, db: SessionLocal = Depends(get_db_sync),
                                            client: UserBase = Depends(get_current_user)):
    """
    선택한 board_id에 대한 dashboard config 삭제 ( config 한개 남았을 시, 삭제 불가)
    """
    db_board_config = db_get_dashboard_config_by_id(db, board_id=board_id)

    if not client.is_superuser:
        if client.user_id != db_board_config.owner_id:
            # raise ex.NotAuthorized
            return {"result":"not allowed"}

    if db_is_my_config_by_id(db=db, board_id=board_id, user_id=client.user_id):
        return {"result": "ERROR! my_config는 삭제 불가"}
    else :
        data = db_delete_dashboard_config_by_id(board_id=board_id, db=db)
        return {"result": "Delete Success!", "data": data}
