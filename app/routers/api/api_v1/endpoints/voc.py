from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.voc import get_voc_event_by_group_date, \
                         get_voc_list_by_group_date, \
                         get_voc_trend_by_group_date, \
                         get_worst10_bts_by_group_date, \
                         get_worst10_hndset_by_group_date, \
                         get_voc_spec_by_srno,\
                         get_voc_trend_item_by_group_date, \
                         get_worst10_bts_by_group_date2, \
                         get_worst10_hndset_by_group_date2, \
                         get_voc_trend_by_group_date2,\
                         get_voc_trend_by_group_date_bk


router = APIRouter()

# 주기지국 VOC 기준 Worst TOP 10
@router.get("/worst2", response_model=List[schemas.VocBtsOutput])
async def get_worst_bts2(limit: int = 10, prod:str=None, code:str=None, group:str="",
                        start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_bts = await get_worst10_bts_by_group_date2(db=db, prod=prod, code=code, group=group,
                                              start_date=start_date, end_date=end_date, limit=limit)
    return worst_bts

# 단말기 VOC 기준 Worst TOP 10
@router.get("/worst_hndset2", response_model=List[schemas.VocHndsetOutput])
async def get_worst_hndset2(limit: int = 10, prod:str=None, code:str=None, group:str="",
                           start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_hndset = await get_worst10_hndset_by_group_date2(db=db, prod=prod, code=code, group=group,
                                                    start_date=start_date, end_date=end_date, limit=limit)
    return worst_hndset

# VOC목록
@router.get("/list", response_model=List[schemas.VocListOutput])
async def get_vocs_detail(limit: int = 1000, group:str="", start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    voc_details = await get_voc_list_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return voc_details

# 기존 Code
# @router.get("/list", response_model=List[schemas.VocListOutput])
# async def get_vocs_detail(limit: int = 1000, team: str = "성남엔지니어링부", start_date: str = "20220510", end_date: str = "20220520", db: SessionLocal = Depends(get_db)):
#     voc_details = get_voc_list_by_group_date(db=db, group=team, start_date=start_date, end_date=end_date, limit=limit)
#     return voc_details

@router.get("/trend-day2", response_model=List[schemas.VocTrendOutput])
async def get_voc_trend_daily2(prod:str=None, code:str=None, group:str="",start_date:str="20220901", end_date:str=None
                              , db: SessionLocal = Depends(get_db)):
    voc_trend_days = await get_voc_trend_by_group_date2(db=db, prod=prod, code=code, group=group,
                                                 start_date=start_date, end_date=end_date)
    return voc_trend_days


# 기존 Code
# @router.get("/trend/day", response_model=List[schemas.VocTrendOutput])
# async def get_voc_trend_daily(team: str = "성남엔지니어링부", start_date: str = "20220510", end_date: str = "20220520", db: SessionLocal = Depends(get_db)):
#     voc_trend_days = get_voc_trend_by_group_date(db=db, group=team, start_date=start_date, end_date=end_date)
#     return voc_trend_days

@router.get("/kpi-day", response_model=schemas.VocEventOutput)
async def get_voc_event_day(prod:str=None, code:str=None,  group:str="", date:str="20220901",
                            db: SessionLocal = Depends(get_db)):
    voc_event_day = await get_voc_event_by_group_date(db=db, prod=prod, code=code, group=group, date=date)
    return voc_event_day


# VOC 상세 - SRTT_RCP_NO에 대한 전일이후 기지국 목록
@router.get("/spec", response_model=schemas.VocSpecOutput)
async def get_voc_spec(limit:int=30, sr_tt_rcp_no:str="SR20220904110027-1-1LV6UUNL", db: SessionLocal = Depends(get_db)):
    voc_spec = await get_voc_spec_by_srno(db=db, sr_tt_rcp_no=sr_tt_rcp_no, limit=limit)
    return voc_spec


@router.get("/trend-item-day", response_model=List[schemas.VocTrendItemOutput])
async def get_voc_trend_item_daily(prod:str=None, code:str=None, group:str="",start_date:str="20220901", end_date:str=None
                              , db: SessionLocal = Depends(get_db)):
    voc_trend_days = await get_voc_trend_item_by_group_date(db=db, prod=prod, code=code, group=group,
                                                 start_date=start_date, end_date=end_date)
    return voc_trend_days


# # 주기지국 Worst TOP 10
# @router.get("/", response_model=List[schemas.JoinVoc])
# async def get_vocs_by_main_bts(limit: int = 10, team: str = None, date: str = None, db: SessionLocal = Depends(get_db)):
#     vocs = get_vocs(db=db, team=team, date=date, limit=limit)
#     return vocs


#############################################
# 주기지국 VOC 기준 Worst TOP 10
@router.get("/worst", response_model=List[schemas.VocBtsOutput])
async def get_worst_bts(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_bts = await get_worst10_bts_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_bts

# 단말기 VOC 기준 Worst TOP 10
@router.get("/worst_hndset", response_model=List[schemas.VocHndsetOutput])
async def get_worst_hndset(limit: int = 10, group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_hndset = await get_worst10_hndset_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return worst_hndset

@router.get("/trend-day", response_model=List[schemas.VocTrendOutput])
async def get_voc_trend_daily(group:str="", start_date: str = "20220501", end_date: str = None, db: SessionLocal = Depends(get_db)):
    voc_trend_days = await get_voc_trend_by_group_date_bk(db=db, group=group, start_date=start_date, end_date=end_date)
    return voc_trend_days

