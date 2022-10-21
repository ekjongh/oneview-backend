from typing import List

from app.errors import exceptions as ex
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.crud.user import create_user, get_users, get_user_by_id, update_user, delete_user
from app.routers.api.deps import get_db, get_current_user, get_current_active_user
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOutput
# from app.schemas.user_board_config import UserBoardConfigBase, UserBoardConfig
# from app.utils.internel.user import dashboard_model_to_schema
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/", response_model=UserBase, status_code=201)
async def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    register_user = get_user_by_id(db, user.user_id)
    if register_user:
        raise HTTPException(status_code=401, detail="user already exist")
    user = create_user(db, user)
    return {"result": True, "user": user}


@router.get("/", response_model=List[UserOutput])
async def read_users(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    users = await get_users(db, skip=skip, limit=limit)
    # print("USERS MODEL: ", users[0].__dict__)
    new_users = []
    for user in users:
        user.__dict__.pop("_sa_instance_state")
        new_users.append(user)
    users_out = list(map(lambda model:UserOutput(**model.__dict__), new_users))
    return users_out

@router.get("/me", response_model=UserOutput)
async def read_my_config(user: UserBase = Depends(get_current_user)):
    if not user:
        return None
    else:
        user_me = UserOutput(**user.__dict__)
        return user_me


@router.put("/me", response_model=UserOutput)
async def update_my_config(user:UserBase = Depends(get_current_user)):
    pass


@router.get("/{id}", response_model=UserOutput)
async def read_user_by_id(id: str, db: SessionLocal = Depends(get_db)):
    db_user = await get_user_by_id(db, user_id=id)
    if db_user is None:
        raise ex.NotFoundUserEx
    print("db_user: ", db_user.__dict__)
    user_out = UserOutput(**db_user.__dict__)
    return user_out

@router.put("/{id}", response_model=UserBase)
async def update_user_by_id(id: str, user:UserOutput, db: SessionLocal = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise ex.NotAuthorized
    _user = await update_user(db, user_id=id, user=user)

    return {"result": "Update Success!", "user": _user}


@router.delete("/{id}", response_model=UserBase)
async def delete_user_by_id(id: int, db: SessionLocal = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise ex.NotAuthorized
    _ = await delete_user(db=db, user_id=id)
    return {"result": "Delete Success!"}

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
# @router.get("/boardconfig/{id}", response_model=UserBoardConfig)
# async def read_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):
#     try:
#         board_configs = get_dashboard_configs_by_id(db, user_id=id)
#         result = dashboard_model_to_schema(board_configs)
#     except:
#         if get_user_by_id(db, user_id=id):
#             board_configs = create_dashboard_config_by_id(db, id=id)
#             result = dashboard_model_to_schema(board_configs)
#         else:
#             raise ex.NotFoundUserEx
#     return result
#
#
# @router.put("/boardconfig/{id}", response_model=UserBoardConfig)
# async def update_dashboard_config_by_id(id: str, board_config: UserBoardConfig, db: SessionLocal = Depends(get_db)):
#     board_configs = update_dashboard_config(id=id, db=db, board_config=board_config)
#     result = dashboard_model_to_schema(board_configs)
#     return result
#
#
# @router.delete("/boardconfig/{id}", response_model=UserBoardConfig)
# async def delete_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):
#     board_configs = delete_dashboard_config(id=id, db=db)
#     result = dashboard_model_to_schema(board_configs)
#     return result