from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import verify_password
from app.crud.blacklist import create_blacklist
from app.crud.user import get_user_by_id, create_user, update_user
from app.crud.dashboard_config import db_insert_dashboard_config_by_default
from app.routers.api.deps import get_db, get_current_active_user, get_current_user, get_db_sync
from app.schemas import UserCreate, TokenCreate
from app.schemas.user import User, UserBase, UserEnc, UserCreate

## 인증테스트
import jpype
from fastapi import Form, Request, Response, status
from starlette.responses import RedirectResponse, HTMLResponse
from app.utils import java
from app.errors.exceptions import AccessEx

router = APIRouter()


@router.post('/jwt/login')
async def login(user: UserBase, db: Session = Depends(get_db_sync), Authorize: AuthJWT = Depends()):
    login_user = get_user_by_id(db, user.user_id)
    if not login_user:
        raise HTTPException(status_code=401,detail="Bad user id")
    if not verify_password(user.password, login_user.hashed_password):
        raise HTTPException(status_code=401,detail="Bad password")

    access_token = Authorize.create_access_token(subject=user.user_id, expires_time=timedelta(minutes=60))
    refresh_token = Authorize.create_refresh_token(subject=user.user_id, expires_time=timedelta(days=1))
    return {"access": access_token, "refresh": refresh_token}


@router.post('/jwt/logout/access')
async def logout_access(db: Session = Depends(get_db_sync), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    _user = get_user_by_id(db, current_user)
    _user_id = _user.user_id

    decrypted_token = Authorize.get_raw_jwt()['jti']
    create_blacklist(db, token=decrypted_token, user_id=_user_id)
    return {"detail": "Access Token Revoke success!"}


@router.post('/jwt/logout/refresh')
async def logout_refresh(db: Session = Depends(get_db_sync), Authorize: AuthJWT = Depends()):
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
    new_access_token = Authorize.create_access_token(subject=current_user, expires_time=timedelta(minutes=60))
    return {"access": new_access_token}




# 복호화 test , pip install python-multipart, pip3 install JPype1, import jpype,form
@router.post('/jwt/auth')
def login_by_kdap(request:Request, VOC_USER_ID: str=Form(...), VOC_CLIENT_IP:str=Form(...), VOC_ORG_NM:str=Form(...), db: Session = Depends(get_db_sync),Authorize: AuthJWT = Depends()):
    client_ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    client_ip_decoded = java.decode_value(VOC_CLIENT_IP)
    user_id_decoded = java.decode_value(VOC_USER_ID)
    org_nm_decoded = java.decode_value(VOC_ORG_NM)
    print(f"AUTH:{user_id_decoded}:{client_ip_decoded}:{client_ip}:{org_nm_decoded}:{datetime.now()}")
    # if client_ip != client_ip_decoded:
    #     raise HTTPException(status_code=401, detail="Bad user ip")
    #    return RedirectResponse(url="/#/fail", status_code=status.HTTP_303_SEE_OTHER)

    login_user = get_user_by_id(db, user_id_decoded)
    if not login_user:
        register_user = UserCreate(user_id = user_id_decoded)
        user = create_user(db, register_user)
        config = db_insert_dashboard_config_by_default(db,user)
        if config :
            _ = update_user(db, user.user_id,
                            schemas.UserUpdate(board_id=config.board_id,
                                               start_board_id=config.board_id),
                            is_superuser=False )

    # access_token = Authorize.create_access_token(subject=user_id_decoded, expires_time=timedelta(minutes=60))
    refresh_token = Authorize.create_refresh_token(subject=user_id_decoded, expires_time=timedelta(days=1))
    r = RedirectResponse(url=f"/#/auth?token={refresh_token}", status_code=status.HTTP_303_SEE_OTHER)
    # r.set_cookie(key="access_token", value=access_token, httponly=False )
    # r.set_cookie(key="refresh_token", value=refresh_token, httponly=False )

    return r



# 복호화 test , pip install python-multipart, pip3 install JPype1, import jpype,form
@router.get('/jwt/auth')
def login_by_kdap(request:Request, db: Session = Depends(get_db_sync)):
    r = RedirectResponse(url=f"/get_error.html", status_code=status.HTTP_303_SEE_OTHER)
    return r


