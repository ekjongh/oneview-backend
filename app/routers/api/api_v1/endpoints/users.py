from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.crud.user import create_user, delete_dashboard_config, get_dashboard_configs, get_dashboard_configs_by_id, get_users, get_user_by_id, update_user, delete_user, create_dashboard_config, update_dashboard_config
from app.routers.api.deps import get_db, get_current_user, get_current_active_superuser, get_current_active_user
from app.schemas.user import User, UserCreate, UserUpdate, UserMe
from app.schemas.user_board_config import UserBoardConfigBase, UserBoardConfig, BoardConfigBase, EventConfigBase
from app.utils.user import dashboard_model_to_schema

router = APIRouter()


@router.post("/", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    register_user = get_user_by_id(db, user.user_id)
    if register_user:
        raise HTTPException(status_code=401, detail="user already exist")
    user = create_user(db, user)
    return {"result": True, "employee_id": user.employee_id}


@router.get("/", response_model=List[UserUpdate])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user:User = Depends(get_current_active_superuser)):
    users = get_users(db, skip=skip, limit=limit)
    users_out = list(map(lambda model:
        UserUpdate(
            id=model.id,
            user_id=model.user_id,
            password=model.hashed_password,
            username=model.username,
            email=model.email,
            phone=model.phone,
            is_active=model.is_active,
            is_superuser=model.is_superuser,

            auth=model.auth,
            belong_1=model.belong_1,
            belong_2=model.belong_2,
            belong_3=model.belong_3,
            belong_4=model.belong_4,
        ), users))
    return users_out


@router.get("/me", response_model=UserMe)
async def read_my_config(user:User = Depends(get_current_user)):
    userMe = UserMe(
        id = user.id,
        username = user.username,
        user_id = user.user_id,
        auth = user.auth,
        belong_1 = user.belong_1,
        belong_2 = user.belong_2,
        belong_3 = user.belong_3,
        belong_4 = user.belong_4,
    )
    return userMe


@router.put("/me", response_model=UserMe)
async def update_my_config(user:User = Depends(get_current_user)):
    pass


@router.get("/{id}", response_model=User)
async def read_user_by_id(id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{id}", response_model=User)
async def update_user_by_id(id: int, user:UserUpdate, db: Session = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise HTTPException(status_code=401, detail="Need Auth...")
    _user = update_user(db, user_id=id, user=user)

    return {"result": "Update Success!", "id": _user.id}


@router.delete("/{id}", response_model=User)
async def delete_user_by_id(id: int, db: Session = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise HTTPException(status_code=401, detail="Need Auth...")
    _ = delete_user(db=db, user_id=id)
    return {"result": "Delete Success!"}

# ------------------------------- User DashBoard Config ... -------------------------------------- #

@router.post("/boardconfig")
async def register_dashboard_config(board_config: UserBoardConfigBase, db: SessionLocal = Depends(get_db)):
    id = board_config.owner_id + "_" + board_config.config_nm
    register_board_config = get_dashboard_configs_by_id(db, id)
    if register_board_config:
        raise HTTPException(status_code=401, detail="user dashboard config already exist")
    new_dashboard_config = create_dashboard_config(db, board_config)
    return {"result": True, "user_id": board_config.owner_id}

@router.get("/boardconfig/all")
async def read_dashboard_all_configs(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    board_configs = get_dashboard_configs(db=db, skip=skip, limit=limit)
    result = [dashboard_model_to_schema(board_config) for board_config in board_configs]

    return result

@router.get("/boardconfig/{id}", response_model=List[UserBoardConfig])
async def read_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):

    board_configs = get_dashboard_configs_by_id(db, user_id=id)
    result = [dashboard_model_to_schema(board_config) for board_config in board_configs]

    return result

@router.put("/boardconfig/{id}")
async def update_dashboard_config_by_id(id: str, board_config: UserBoardConfig, db: SessionLocal = Depends(get_db)):
    rst = update_dashboard_config(id=id, db=db, board_config=board_config)
    return {"result": rst}

@router.delete("/boardconfig/{id}")
async def delete_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):
    rst = delete_dashboard_config(id=id, db=db)
    return {"result": rst}