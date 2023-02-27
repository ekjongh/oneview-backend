from typing import List, Tuple

from fastapi import APIRouter, Depends

from app import schemas
from app.db.session import SessionLocal
from app.routers.api.deps import get_db
from app.crud.voc import get_voc_list_by_group_date, \
                         get_voc_spec_by_srno,\
                         get_voc_trend_item_by_group_date, \
                         get_worst10_bts_by_group_date, \
                         get_worst10_hndset_by_group_date, \
                         get_voc_trend_by_group_date, \
                         get_voc_trend_by_group_month, \
                         get_voc_trend_item_by_group_month, \
                         get_voc_trend_by_group_hour_stack,\
                         get_voc_summary_by_group_date, \
                         get_voc_count_item_by_group_hour


router = APIRouter()

# 주기지국 VOC 기준 Worst TOP 10
@router.get("/worst", response_model=List[schemas.VocBtsOutput])
async def get_worst_bts(limit: int = 10, prod:str=None, code:str=None, group:str="", band:str=None,
                        start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_bts = await get_worst10_bts_by_group_date(db=db, prod=prod, code=code, group=group, band=band,
                                              start_date=start_date, end_date=end_date, limit=limit)
    return worst_bts

# 단말기 VOC 기준 Worst TOP 10
@router.get("/worst-hndset", response_model=List[schemas.VocHndsetOutput])
async def get_worst_hndset(limit: int = 10, prod:str=None, code:str=None, group:str="",
                           start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    worst_hndset = await get_worst10_hndset_by_group_date(db=db, prod=prod, code=code, group=group,
                                                    start_date=start_date, end_date=end_date, limit=limit)
    return worst_hndset

# VOC목록
@router.get("/list", response_model=List[schemas.VocListOutput])
async def get_vocs_detail(limit: int = 1000, group:str="", start_date: str = "20220901", end_date: str = None, db: SessionLocal = Depends(get_db)):
    voc_details = await get_voc_list_by_group_date(db=db, group=group, start_date=start_date, end_date=end_date, limit=limit)
    return voc_details


@router.get("/trend-day", response_model=List[schemas.VocTrendOutput])
async def get_voc_trend_daily(prod:str=None, code:str=None, group:str="",start_date:str="20220901", end_date:str=None
                              , db: SessionLocal = Depends(get_db)):
   voc_trend_days = await get_voc_trend_by_group_date(db=db, prod=prod, code=code, group=group,
                                                 start_date=start_date, end_date=end_date)
   return voc_trend_days


@router.get("/summary-day", response_model=schemas.VocSummaryOutput)
async def get_voc_summary_daily(code:str=None, group:str="",start_date:str="20220901",
                               db: SessionLocal = Depends(get_db)):
    voc_trend_days = await get_voc_summary_by_group_date(db=db, code=code, group=group,
                                                            start_date=start_date)

    return voc_trend_days


# VOC 상세 - SRTT_RCP_NO에 대한 전일이후 기지국 목록
@router.get("/spec", response_model=schemas.VocSpecOutput)
async def get_voc_spec(limit:int=30, sr_tt_rcp_no:str="SR20220904110027-1-1LV6UUNL", db: SessionLocal = Depends(get_db)):
    voc_spec = await get_voc_spec_by_srno(db=db, sr_tt_rcp_no=sr_tt_rcp_no, limit=limit)
    return voc_spec


@router.get("/trend-item-day", response_model=List[schemas.VocTrendItemOutput])
async def get_voc_trend_item_daily(prod:str=None, code:str=None, group:str="", by:str="code",
                                   start_date:str="20220901", end_date:str=None, db: SessionLocal = Depends(get_db)):
    voc_trend_days = await get_voc_trend_item_by_group_date(db=db, prod=prod, code=code, group=group, by=by,
                                                 start_date=start_date, end_date=end_date)
    return voc_trend_days

@router.get("/trend-month", response_model=List[schemas.VocTrendMonthOutput])
async def get_voc_trend_month(prod:str=None, code:str=None, group:str="",start_month:str="202101", end_month:str=None
                              , db: SessionLocal = Depends(get_db)):
    """
    천회선당VOC(월별)
    - code: 본부,센터별,팀별,시도별,시군구별
    - out: date,value(천회선당voc), voc_cnt, sbscr_cnt
    """
    voc_trend_months = await get_voc_trend_by_group_month(db=db, prod=prod, code=code, group=group,
                                                 start_month=start_month, end_month=end_month)
    return voc_trend_months


@router.get("/trend-item-month", response_model=List[schemas.VocTrendItemMonthOutput])
async def get_voc_trend_item_month(prod:str=None, code:str=None, group:str="",by:str="code",
                                   start_month:str="202101", end_month:str=None, db: SessionLocal = Depends(get_db)):
    """
    천회선당VOC(월별) group 비교 그래프

    code: 본부,센터별,팀별,시도별,시군구별
    out: date,value(천회선당voc), voc_cnt, sbscr_cnt
        
    """
    voc_trend_month = await get_voc_trend_item_by_group_month(db=db, prod=prod, code=code, group=group,by=by,
                                                 start_month=start_month, end_month=end_month)
    return voc_trend_month


@router.get("/trend-hour-stack", response_model=List[schemas.VocHourTrendOutput])
async def get_voc_trend_hour_stack(prod:str=None, code:str=None, group:str="",start_date:str="20230215",
                               db: SessionLocal = Depends(get_db)):
    """
    천회선당VOC(월별)
    - code: 본부,센터별,팀별,시도별,시군구별
    - out: date,value(천회선당voc), voc_cnt, sbscr_cnt
    """
    voc_trend_hour = await get_voc_trend_by_group_hour_stack(db=db, prod=prod, code=code, group=group,
                                                 start_date=start_date)
    return voc_trend_hour

@router.get("/count-item-hour", response_model=List[schemas.VocHourTrendItemOutput])
async def get_voc_count_item_hour(prod:str=None, code:str=None, group:str="",start_date:str="20230214",
                               by:str=None, db: SessionLocal = Depends(get_db)):
    """
    아이템별VOC건수(시간별)
    - code: 본부별, 센터별,시도별,시군구별,읍면동별   (팀별,조별,)
    - by : 유형대, 유형중, 유형소, 단말기종, SA구분, 시군구 
    - out: hour, sub_item1, sub_item2, sub_item3 ...
    """
    voc_count_hour = await get_voc_count_item_by_group_hour(db=db, prod=prod, code=code, group=group,
                                                 start_date=start_date, by=by)
    return voc_count_hour