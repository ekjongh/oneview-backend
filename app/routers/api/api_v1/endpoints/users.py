from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.crud.user import create_user, get_dashboard_configs, get_dashboard_configs_by_id, get_users, get_user_by_id, update_user, delete_user, create_dashboard_config, update_dashboard_config
from app.routers.api.deps import get_db, get_current_user, get_current_active_user
from app.schemas.user import User, UserCreate, UserUpdate, UserOutput
from app.schemas.user_board_config import UserBoardConfigBase, UserBoardConfig
from app.utils.internel.user import dashboard_model_to_schema

router = APIRouter()


@router.post("/", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    register_user = get_user_by_id(db, user.user_id)
    if register_user:
        raise HTTPException(status_code=401, detail="user already exist")
    user = create_user(db, user)
    return {"result": True, "user": user}


@router.get("/", response_model=List[UserOutput])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    users_out = list(map(lambda model:UserOutput(**model.__dict__), users))
    return users_out


@router.get("/me", response_model=UserOutput)
async def read_my_config(user: User = Depends(get_current_user)):
    user_me = UserOutput(**user.__dict__)
    # user_me = UserOutput(
    #     user_name = user.user_name,
    #     user_id = user.user_id,
    #     auth = user.auth,
    #     belong_1 = user.belong_1,
    #     belong_2 = user.belong_2,
    #     belong_3 = user.belong_3,
    #     belong_4 = user.belong_4,
    # )
    return user_me


@router.put("/me", response_model=UserOutput)
async def update_my_config(user:User = Depends(get_current_user)):
    pass


@router.get("/{id}", response_model=User)
async def read_user_by_id(id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{id}", response_model=User)
async def update_user_by_id(id: str, user:UserOutput, db: Session = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise HTTPException(status_code=401, detail="Need Auth...")
    _user = update_user(db, user_id=id, user=user)

    return {"result": "Update Success!", "user": _user}


@router.delete("/{id}", response_model=User)
async def delete_user_by_id(id: int, db: Session = Depends(get_db),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise HTTPException(status_code=401, detail="Need Auth...")
    _ = delete_user(db=db, user_id=id)
    return {"result": "Delete Success!"}

# ------------------------------- User DashBoard Config ... -------------------------------------- #


@router.get("/boardconfig/all")
async def read_dashboard_all_configs(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    board_configs = get_dashboard_configs(db=db, skip=skip, limit=limit)
    result = [dashboard_model_to_schema(board_config) for board_config in board_configs]
    return result


@router.get("/boardconfig/{id}", response_model=UserBoardConfig)
async def read_dashboard_config_by_id(id: str, db: SessionLocal = Depends(get_db)):
    board_configs = get_dashboard_configs_by_id(db, user_id=id)
    result = dashboard_model_to_schema(board_configs)
    return result


@router.put("/boardconfig/{id}", response_model=UserBoardConfig)
async def update_dashboard_config_by_id(id: str, board_config: UserBoardConfig, db: SessionLocal = Depends(get_db)):
    board_configs = update_dashboard_config(id=id, db=db, board_config=board_config)
    result = dashboard_model_to_schema(board_configs)
    return result