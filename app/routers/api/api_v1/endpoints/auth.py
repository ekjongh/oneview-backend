from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import verify_password
from app.crud.blacklist import create_blacklist
from app.crud.user import get_user_by_id, create_user
from app.routers.api.deps import get_db, get_current_active_user, get_current_user
from app.schemas import UserCreate, TokenCreate
from app.schemas.user import User, UserBase


router = APIRouter()



@router.post('/jwt/login')
async def login(user: UserBase, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    login_user = get_user_by_id(db, user.user_id)
    if not login_user:
        raise HTTPException(status_code=401,detail="Bad user id")
    if not verify_password(user.password, login_user.hashed_password):
        raise HTTPException(status_code=401,detail="Bad password")

    access_token = Authorize.create_access_token(subject=user.user_id)
    refresh_token = Authorize.create_refresh_token(subject=user.user_id)
    return {"access": access_token, "refresh": refresh_token}


@router.post('/jwt/logout/access')
async def logout_access(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    _user = get_user_by_id(db, current_user)
    _user_id = _user.user_id

    decrypted_token = Authorize.get_raw_jwt()['jti']
    create_blacklist(db, token=decrypted_token, user_id=_user_id)
    return {"detail": "Access Token Revoke success!"}


@router.post('/jwt/logout/refresh')
async def logout_refresh(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()

    _user = get_user_by_id(db, current_user)

    _user_id = _user.user_id
    decrypted_token = Authorize.get_raw_jwt()['jti']

    db_blacklist = create_blacklist(db, token=decrypted_token, user_id=_user_id)
    return {"detail": db_blacklist}


# @router.delete('/jwt/logout/access')
# async def logout(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     jti = Authorize.get_raw_jwt()['jti']
#     current_user_employee_id = Authorize.get_jwt_subject()
#     logout_user = get_user_by_employee_id(db, current_user_employee_id)
#     create_blacklist(db=db, token=schemas.TokenCreate(jti), user_id=logout_user.id)
#     return {"detail": "Access Token has been revoke"}
#
#
# @router.delete('/jwt/logout/refresh')
# async def logout(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_refresh_token_required()
#     jti = Authorize.get_raw_jwt()['jti']
#     current_user_employee_id = Authorize.get_jwt_subject()
#     logout_user = get_user_by_employee_id(db, current_user_employee_id)
#     create_blacklist(db=db, token=schemas.TokenCreate(jti), user_id=logout_user.id)
#     return {"detail": "Refresh Token has been revoke"}


# @router.post('/jwt/logout')
# async def logout(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     employee_id = Authorize.get_jwt_subject()
#     user = get_user_by_employee_id(db, employee_id)
#     _ = Authorize.create_access_token(subject=user.employee_id, expires_time=0)
#     _ = Authorize.create_refresh_token(subject=user.employee_id, expires_time=0)
#     return {"detail": "Logout Success!"}

# @router.post('/jwt/users')
# async def register(user: UserCreate, db: Session = Depends(get_db)):
#     register_user = get_user_by_employee_id(db, user.employee_id)
#     if register_user:
#         raise HTTPException(status_code=401, detail="user already exist")
#     user = create_user(db, user)
#     return {"state": True, "employee_id": user.employee_id}


@router.post('/jwt/refresh')
async def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access": new_access_token}