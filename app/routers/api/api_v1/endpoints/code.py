from typing import List, Tuple

from fastapi import APIRouter, Depends

from app.errors import exceptions as ex
from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.code import \
    get_addr_code_all, \
    get_org_code_all, \
    get_menu_code_all
    # get_dashboard_configs, \
    # update_dashboard_config, \
    # delete_dashboard_config, \
    # create_dashboard_config
from app.routers.api.deps import get_current_active_user

router = APIRouter()


@router.get("/addr", response_model=List[schemas.AddrCodeOutput])
async def get_addr_code(sido:str=None, gungu:str=None, dong:str=None, db: SessionLocal = Depends(get_db)):
    return await get_addr_code_all(sido=sido, gungu=gungu, dong=dong, db=db)


@router.get("/org")
async def get_org_code(db: SessionLocal = Depends(get_db)):
    return await get_org_code_all(db=db)


@router.get("/menu", response_model=List[schemas.MenuCodeOutput])
async def get_menu_code(db: SessionLocal = Depends(get_db)):
    return await get_menu_code_all(db=db)


@router.get("/cmpn")
async def get_maker_code():
    maker_list = ["삼성전자", "노키아", "에릭슨엘지(주)", "이노와이어리스", "(주)주니코리아"]
    return maker_list


# # ------------------------------- User DashBoard Config ... -------------------------------------- #
#
#
# @router.get("/boardconfigs", response_model=List[schemas.ConfigCode])
# async def read_dashboard_all_configs(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
#     """
#     사용자 대시보드 설정 전체 가져오기(관리자 페이지용)
#     :param skip:
#     :param limit:
#     :return: List(board_config)
#     """
#     board_configs = await get_dashboard_configs(db=db, skip=skip, limit=limit)
#     # result = [dashboard_model_to_schema(board_config) for board_config in board_configs]
#     return board_configs
#
# # @router.get("/boardconfig/{id}", response_model=UserBoardConfig)
# # async def read_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):
# #     try:
# #         board_configs = get_dashboard_configs_by_id(db, user_id=id)
# #         result = dashboard_model_to_schema(board_configs)
# #     except:
# #         if get_user_by_id(db, user_id=id):
# #             board_configs = create_dashboard_config_by_id(db, id=id)
# #             result = dashboard_model_to_schema(board_configs)
# #         else:
# #             raise ex.NotFoundUserEx
# #     return result
# #
# #
# @router.put("/boardconfig/{idx}")
# async def update_dashboard_config_by_idx(idx: int, board_config: schemas.ConfigCode, db: SessionLocal = Depends(get_db), client=Depends(get_current_active_user)):
#     if not client.is_superuser:
#         raise ex.NotAuthorized
#
#     _ = await update_dashboard_config(idx=idx, db=db, board_config=board_config)
#     # result = dashboard_model_to_schema(board_configs)
#     return {"result":"update_success"}
#
#
# @router.delete("/boardconfig/{idx}")
# async def delete_dashboard_config_by_idx(idx: int, db: SessionLocal = Depends(get_db)):
#     _ = await delete_dashboard_config(idx=idx, db=db)
#     # result = dashboard_model_to_schema(board_configs)
#     return {"result":"delete_success"}
#
#
# @router.post("/boardconfig",  status_code=201)
# async def register(board_config: schemas.ConfigCode, db: SessionLocal = Depends(get_db)):
#
#     result = await create_dashboard_config(db, board_config)
#     return {"result": "create_success", "board_config": result}