from html import entities
from sqlalchemy.orm import Session
from app import schemas
from sqlalchemy import func, select, between
from datetime import datetime, timedelta

from .. import models


def get_worst10_bts_by_group_date(db: Session, group:str=None, start_date: str=None, end_date: str=None, limit: int=10):

    voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
    juso = func.concat(models.VocList.sido_nm, models.VocList.eup_myun_dong_nm).label("juso")
    
    entities = [
        models.VocList.equip_cd0.label("기지국명"),
        juso,
        models.VocList.area_center_nm.label("center"),
        models.VocList.bts_oper_team_nm.label("team"),
        models.VocList.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)
    
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc())
    
    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_bts


def get_voc_list_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=1000):

    entities=[
        models.VocList.base_date.label("기준년원일"),
        models.VocList.sr_tt_rcp_no.label("VOC접수번호"),
        models.VocList.voc_type_nm.label("VOC유형"),
        models.VocList.voc_wjt_scnd_nm.label("VOC2차업무유형"),
        models.VocList.voc_wjt_tert_nm.label("VOC3차업무유형"),
        models.VocList.voc_wjt_qrtc_nm.label("VOC4차업무유형"),
        models.VocList.svc_cont_id.label("서비스계약번호"),
        models.VocList.hndset_pet_nm.label("단말기명"),
        models.VocList.anals_5_prod_level_nm.label("분석상품레벨3"),
        models.VocList.bprod_nm.label("요금제"),
        models.VocList.equip_cd0.label("주기지국"),
        models.VocList.area_center_nm.label("주기지국센터"),
        models.VocList.bts_oper_team_nm.label("주기지국팀"),
        models.VocList.area_jo_nm.label("주기지국조")
    ]
    stmt = select(*entities)
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)

    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()
    list_voc_list = list(map(lambda x: schemas.VocListOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_list


def get_voc_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("value")

    entities = [
        models.VocList.base_date.label("date")
    ]
    entities_groupby = [
        voc_cnt
    ]

    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)
    
    stmt = stmt.group_by(*entities).order_by(models.VocList.base_date.asc())

    query = db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend


def get_voc_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
    
    today = date
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")  
    in_cond = [yesterday, today]

    voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")

    entities = [
        models.VocList.base_date,
        models.VocList.bts_oper_team_nm,
        models.VocList.area_jo_nm
    ]
    entities_groupby = [
        voc_cnt
    ]

    stmt = select([*entities, *entities_groupby], models.VocList.base_date.in_(in_cond)).\
            group_by(*entities).order_by(models.VocList.base_date.asc())
    
    stmt = stmt.where(models.VocList.area_jo_nm == group)

    query = db.execute(stmt)
    query_result = query.all()
    # query_keys = query.keys()

    try:
        yesterday_score = query_result[0][3]
        today_score = query_result[1][3]
        event_rate = (today_score - yesterday_score) / yesterday_score * 100
    except:
        return None

    voc_event = schemas.VocEventOutput(
        title= "품질VOC 발생건수(전일대비)",
        score= today_score,
        rate= event_rate
    )
    return voc_event
