########################################################################################################################
# 라우팅 테이블 정의
#
# [ 라우팅 테이블 구조 설명 ]
# app/routers/api/api_v1/           ./endpoints/
# api.py                            voc.py
# ┌---------------┐                 ┌---------------------------------------┐
# | /api/v1/voc   |---------------->| /worst2                               |
# | (tags = voc   |                 | async def get_worst_bts2():           |
# └---------------┘                 |   get_worst10_bts_by_group_date2() ---┼---------------┐
#                                   |                                       |               |
#                                   | /worst_hndset2                        |               |
#                                   | async def get_worst_hndset2()         |               |
#                                   | .....                                 |               |
#                                   └---------------------------------------┘               |
#                                                                                           |
#                                   app/crud/                                               |
#                                   voc.py                                                  |
#                                   ┌-----------------------------------------------┐       |
#                                   | async def get_worst10_bts_by_group_date2(): <-┤-------┘
#                                   |   ....                                        |
#                                   |  return list_worst_voc_bts                    |
#                                   |                                               |
#                                   | async def get_worst10_hndset_by_group_date2() |
#                                   |   ...                                         |
#                                   └-----------------------------------------------┘
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.16 주석추가
#
########################################################################################################################
from fastapi import APIRouter, Depends
from .endpoints import auth, users, items, voc, volte, events, offloading, mdt, subscr, rrc, data_cnt, code, boardconfig
from ..deps import get_current_user

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router, prefix="/api/v1", tags=["auth"])
api_v1_router.include_router(users.router, prefix="/api/v1/users", tags=["users"])
api_v1_router.include_router(boardconfig.router, prefix="/api/v1/users", tags=["users"])
# api_v1_router.include_router(events.router, prefix="/api/v1/events", tags=["events"])
api_v1_router.include_router(voc.router, prefix="/api/v1/voc", tags=["voc"])
api_v1_router.include_router(volte.router, prefix="/api/v1/volte", tags=["volte"])
api_v1_router.include_router(offloading.router, prefix="/api/v1/offloading", tags=["offloading"])
api_v1_router.include_router(mdt.router, prefix="/api/v1/mdt", tags=["mdt"])
api_v1_router.include_router(subscr.router, prefix="/api/v1/subscr", tags=["subscr"])
api_v1_router.include_router(rrc.router, prefix="/api/v1/rrc", tags=["rrc"])
api_v1_router.include_router(data_cnt.router, prefix="/api/v1/data-usage", tags=["data-usage"])
api_v1_router.include_router(code.router, prefix="/api/v1/code", tags=["code"])

api_v1_router.include_router(items.router, prefix="/api/v1/items", tags=["items"])