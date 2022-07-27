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
        models.VocList.equip_cd0,
        juso,
        models.VocList.area_center_nm,
        models.VocList.bts_oper_team_nm,
        models.VocList.area_jo_nm
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
    
    query_result = db.execute(stmt).fetchmany(size=limit)
    list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(
                                기지국명=x[0],
                                voc_cnt=x[5],
                                juso=x[1],
                                center=x[2],
                                team=x[3],
                                jo=x[4]
                                ), query_result))
    return list_worst_voc_bts

# 기존 Code
# def get_worst10_bts_by_group_date(db: Session, group: str=None, start_date: str=None, end_date: str=None, limit: int=10):
#     voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
#     voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
#     juso = func.concat(models.VocList.sido_nm, models.VocList.eup_myun_dong_nm).label("juso")
    
#     entities = [
#         models.VocList.equip_cd0,
#         juso,
#         models.VocList.bts_oper_team_nm,
#         models.VocList.adm_cd1
#     ]
#     entities_groupby = [
#         voc_cnt
#     ]
#     stmt = select(*entities, *entities_groupby)
    
#     if not end_date:
#         end_date = start_date
        
#     if start_date:
#         stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
#     if group:
#         stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
    
#     stmt = stmt.group_by(*entities).order_by(voc_cnt.desc())
    
#     query_result = db.execute(stmt).fetchmany(size=limit)
#     list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(
#                                 기지국명 = x[0],
#                                 voc_cnt= x[4],
#                                 juso=x[1],
#                                 team= x[2],
#                                 jo= x[3]
#                                 ), query_result))
#     return list_worst_voc_bts

def get_voc_list_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=1000):
    entities=[
        models.VocList.base_date,
        models.VocList.sr_tt_rcp_no,
        models.VocList.voc_type_nm,
        models.VocList.voc_wjt_scnd_nm,
        models.VocList.voc_wjt_tert_nm,
        models.VocList.voc_wjt_qrtc_nm,
        models.VocList.svc_cont_id,
        models.VocList.hndset_pet_nm,
        models.VocList.anals_5_prod_level_nm,
        models.VocList.bprod_nm,
        models.VocList.equip_cd0,
        models.VocList.area_center_nm,
        models.VocList.bts_oper_team_nm,
        models.VocList.area_jo_nm
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

    query_result = db.execute(stmt).fetchmany(size=limit)
    list_voc_list = list(map(lambda x: schemas.VocListOutput(
                                기준년원일= x[0],
                                VOC접수번호=x[1],
                                VOC유형=x[2],
                                VOC2차업무유형=x[3],
                                VOC3차업무유형=x[4],
                                VOC4차업무유형=x[5],
                                서비스계약번호=x[6],
                                단말기명=x[7],
                                분석상품레벨3=x[8],
                                요금제=x[9],
                                # TT번호: Union[str, None]
                                # TT발행주소: Union[str, None]
                                # 상담처리내역: Union[str, None]
                                주기지국=x[10],
                                주기지국센터=x[11],
                                주기지국팀=x[12],
                                주기지국조=x[13],
                                ), query_result))
    return list_voc_list

# 기존 Code
# def get_voc_list_by_group_date(db: Session, group: str=None, start_date: str=None, end_date: str=None, limit: int=1000):
#     entities=[
#         models.VocList.base_date,
#         models.VocList.sr_tt_rcp_no,
#         models.VocList.voc_type_nm,
#         models.VocList.voc_wjt_scnd_nm,
#         models.VocList.voc_wjt_tert_nm,
#         models.VocList.voc_wjt_qrtc_nm,
#         models.VocList.svc_cont_id,
#         models.VocList.hndset_pet_nm,
#         models.VocList.anals_5_prod_level_nm,
#         models.VocList.bprod_nm,
#         models.VocList.equip_cd0,
#         models.VocList.bts_oper_team_nm,
#         models.VocList.adm_cd1,
#     ]
#     stmt = select(*entities)
#     if not end_date:
#         end_date = start_date
        
#     if start_date:
#         stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
#     if group:
#         stmt = stmt.where(models.VocList.bts_oper_team_nm == group)

#     query_result = db.execute(stmt).fetchmany(size=limit)
#     list_voc_list = list(map(lambda x: schemas.VocListOutput(
#                                 기준년원일= x[0],
#                                 VOC접수번호= x[1],
#                                 VOC유형= x[2],
#                                 VOC2차업무유형= x[3],
#                                 VOC3차업무유형= x[4],
#                                 VOC4차업무유형= x[5],
#                                 서비스계약번호= x[6],
#                                 단말기명= x[7],
#                                 분석상품레벨3= x[8],
#                                 요금제= x[9],
#                                 # TT번호: Union[str, None]
#                                 # TT발행주소: Union[str, None]
#                                 # 상담처리내역: Union[str, None]
#                                 주기지국= x[10],
#                                 주기지국팀= x[11],
#                                 주기지국조= x[12],
#                                 ), query_result))
#     return list_voc_list

def get_voc_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")

    entities = [
        models.VocList.base_date
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
    query_result = db.execute(stmt).all()
    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(
                                date=x[0],
                                value=int(x[1])
                                ), query_result))
    print(query_result)
    return list_voc_trend

# 기존 Code
# def get_voc_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
#     voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
#     voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")

#     entities = [
#         models.VocList.base_date
#     ]
#     entities_groupby = [
#         voc_cnt
#     ]

#     stmt = select(*entities, *entities_groupby)
    
#     if not end_date:
#         end_date = start_date
        
#     if start_date:
#         stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
#     stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
    
#     stmt = stmt.group_by(*entities, models.VocList.bts_oper_team_nm).order_by(models.VocList.base_date.asc())
#     query_result = db.execute(stmt).all()
#     list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(
#                                 date=x[0],
#                                 value=int(x[1])
#                                 ), query_result))
#     return list_voc_trend

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

    query_result = db.execute(stmt).all()

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

# 기존 Code
# def get_voc_event_by_group_date(db: Session, group: str, date:str=None):
#     # today = datetime.today().strftime("%Y%m%d")
#     # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
#     today = date
#     yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")  
#     in_cond = [yesterday, today]

#     voc_cnt = func.sum(func.nvl(models.VocList.wjxbfs1, 0))
#     voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")

#     entities = [
#         models.VocList.base_date,
#         models.VocList.bts_oper_team_nm
#     ]
#     entities_groupby = [
#         voc_cnt
#     ]

#     stmt = select([*entities, *entities_groupby], models.VocList.base_date.in_(in_cond)).\
#             where(models.VocList.bts_oper_team_nm == group).group_by(*entities).order_by(models.VocList.base_date.asc())
#     query_result = db.execute(stmt).all()

#     try:
#         yesterday_score = query_result[0][2]
#         today_score = query_result[1][2]
#         event_rate = (today_score - yesterday_score) / yesterday_score * 100
#     except:
#         return None

#     voc_event = schemas.VocEventOutput(
#         title= "품질VOC 발생건수(전일대비)",
#         score= today_score,
#         rate= event_rate
#     )
#     return voc_event