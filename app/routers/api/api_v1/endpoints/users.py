from typing import List

from app.errors import exceptions as ex
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, SessionLocalSync

from app.crud.user import create_user, get_users, get_user_by_id, update_user, delete_user
from app.crud.dashboard_config import db_get_dashboard_config_by_id
from app.routers.api.deps import get_db, get_current_user, get_current_active_user, get_db_sync
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserOutput
# from app.utils.internel.user import dashboard_model_to_schema
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/", response_model=UserBase, status_code=201)
def register(user: UserCreate, db: SessionLocal = Depends(get_db_sync)):
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
def read_my_config(user: UserBase = Depends(get_current_user), db: SessionLocal = Depends(get_db_sync)):
    if not user:
        return None
    else:
        user_me = UserOutput(**user.__dict__)
        board_config = db_get_dashboard_config_by_id(db=db, board_id=user.board_id, user=user)
        if board_config:
            user_me.board_modules= board_config.board_module
        return user_me


@router.put("/me", response_model=UserBase)
def update_my_config(user_in:UserUpdate, db: SessionLocal = Depends(get_db_sync), user:UserBase = Depends(get_current_user)):
    if not user:
        return {"result": "Update Fail!"}
    _user = update_user(db=db, user_id=user.user_id, user=user_in)

    return {"result": "Update Success!", "user": _user}


@router.get("/{id}", response_model=UserOutput)
def read_user_by_id(id: str, db: SessionLocal = Depends(get_db_sync)):
    db_user = get_user_by_id(db, user_id=id)
    if db_user is None:
        raise ex.NotFoundUserEx
    user_out = UserOutput(**db_user.__dict__)
    # user_out = UserOutput(**db_user)
    return user_out


@router.put("/{id}", response_model=UserBase)
def update_user_by_id(id: str, user:UserUpdate, db: SessionLocal = Depends(get_db_sync),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.user_id != id:
            raise ex.NotAuthorized
    _user = update_user(db, user_id=id, user=user)

    return {"result": "Update Success!", "user": _user}


@router.delete("/{id}", response_model=UserBase)
def delete_user_by_id(id: int, db: SessionLocal = Depends(get_db_sync),
                      client=Depends(get_current_active_user)):
    if not client.is_superuser:
        if client.id != id:
            raise ex.NotAuthorized
    _ = delete_user(db=db, user_id=id)
    return {"result": "Delete Success!"}

