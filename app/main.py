from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .crud.blacklist import get_blacklist
from .db.init_db import init_db
from .db.session import SessionLocal, engine
from .middleware.trust_hosts import TrustedHostMiddleware
from .routers.api.api_v1.api import api_v1_router
from pydantic import BaseModel
from .core.security import JWT_SECRET_CODE
from .core.config import conf
from .middleware.validator import access_control


app = FastAPI(debug=True)
c = conf()
conf_dict = c.__dict__

# DB 초기화
init_db(SessionLocal())
# 미들웨어 추가.
origins = [
    "http://localhost:8080",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://10.200.242.253",
    "http://10.200.242.253:8080",
    "http://10.203.13.202",
    "http://10.203.13.202:8242",
    "http://10.203.13.202:8310",
    "http://10.203.13.202:8311",
    "http://10.214.168.57",
    "http://10.214.168.57:8080",
    "http://10.203.228.81:8080",
    "http://10.214.168.57",
    "http://10.214.168.57:8080",
]

app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET_CODE
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    access_expires = timedelta(minutes=60)
    refresh_expires = timedelta(days=1)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    try:
        db = SessionLocal()
        token = get_blacklist(db, jti)
    except:
        raise HTTPException(status_code=404, detail="DB Not Con")
    return not not token

app.include_router(api_v1_router)
# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response
