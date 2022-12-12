import base64
import hmac
import time
import typing
import re

import jwt
import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.errors import exceptions as ex

# # from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
# from app.database.conn import db
# from app.database.schema import Users, ApiKeys
#
# from app.common import config, consts
from app.errors.exceptions import APIException, SqlFailureEx, APIQueryStringEx
# from app.models import UserToken

from app.utils.date_utils import D
from app.utils.logger import api_logger
# from app.utils.query_utils import to_dict

EXCEPT_PATH_LIST = ["/", "/openapi.json"]
EXCEPT_PATH_REGEX = "^(/docs|/redoc|/api/auth)"
JWT_SECRET_CODE="3f9a7d88f906b66122b9288fda701915d42accd31221ac524c3b3afcbc4b3f65"
JWT_ALGORITHM = "HS256"

async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user_agent = None
    request.state.user = None
    request.state.service = None

    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.user_agent = request.headers["user-agent"] if "user-agent" in request.headers.keys() else "None"
    request.state.ip = ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    # cookies = request.cookiesTokenDecodeEx

    url = request.url.path
    # if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
    #     response = await call_next(request)
    #     if url != "/":
    #         await api_logger(request=request, response=response)
    #     return response

    try:
        if url.startswith("/api/v1/jwt") or request.method != "GET":
            res = await call_next(request)
            await api_logger(request=request, response=res)
            return res
        else:
            res = await call_next(request)
            return res

    except Exception as e:
        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        res = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)
    return res


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def exception_handler(error: Exception):
    print(error)
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = SqlFailureEx(ex=error)
    if not isinstance(error, APIException):
        error = APIException(ex=error, detail=str(error))
    return error


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=JWT_SECRET_CODE, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload
