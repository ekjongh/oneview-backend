from html import entities
from sqlalchemy.orm import Session
from app import schemas
from sqlalchemy import func, select, between, case, and_
from datetime import datetime, timedelta

from .. import models


def get_worst10_bts_by_group_date(db: Session, group:str=None, start_date: str=None, end_date: str=None, limit: int=10):
    # 기지국별 5G품질 VOC Worst TOP 10
    voc_cnt = func.sum(func.nvl(models.VocList.sr_tt_rcp_no_cnt, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("VOC건수")
    juso = func.concat(models.VocList.sido_nm+' ', models.VocList.eup_myun_dong_nm).label("juso")
    
    entities = [
        models.VocList.equip_cd.label("기지국ID"),
        models.VocList.equip_nm.label("기지국명"),
        # juso,
        # models.VocList.biz_hq_nm.label("center"),
        # models.VocList.oper_team_nm.label("team"),
        # models.VocList.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(
                *entities, *entities_groupby
            ).where( 
                models.VocList.anals_3_prod_level_nm == '5G'
            )
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.biz_hq_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)
    
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc())

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.VOC건수.desc()).label('RANK'),
        *stmt.c,
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_bts


def get_worst10_hndset_by_group_date(db: Session, group: str = None, start_date: str = None, end_date: str = None,
                                  limit: int = 10):
    # 단말별 5G품질 VOC Worst TOP10
    voc_cnt = func.sum(func.nvl(models.VocList.sr_tt_rcp_no_cnt, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("VOC건수")
   
    entities = [
        models.VocList.hndset_pet_nm.label("단말기명"),
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(
                *entities, *entities_groupby
            ).where(
                models.VocList.anals_3_prod_level_nm == '5G'
            )

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.biz_hq_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.oper_team_nm == group)

    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)

    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.VOC건수.desc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_voc_hndset = list(map(lambda x: schemas.VocHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_hndset

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
        models.VocList.anals_3_prod_level_nm.label("분석상품레벨3"),
        models.VocList.bprod_nm.label("요금제"),
        models.VocList.equip_nm.label("주기지국"),
        models.VocList.biz_hq_nm.label("주기지국센터"),
        models.VocList.oper_team_nm.label("주기지국팀"),
        models.VocList.area_jo_nm.label("주기지국조")
    ]
    stmt = select(*entities)
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.biz_hq_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)

    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()
    list_voc_list = list(map(lambda x: schemas.VocListOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_list


def get_voc_trend_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None):
    # 1000가입자당 5G VOC건수
    voc_cnt = func.sum(func.nvl(models.VocList.sr_tt_rcp_no_cnt, 0)).label("voc_cnt")
    sbscr_cnt = func.sum(func.nvl(models.Subscr.bprod_maint_sbscr_cascnt, 0)).label("sbscr_cnt")

    stmt_sbscr = select(
            models.Subscr.base_date,
            sbscr_cnt
        ).where(
            models.Subscr.anals_3_prod_level_nm == '5G'
        )
    stmt_voc = select(
            models.VocList.base_date,
            voc_cnt
        ).where(
            models.VocList.anals_3_prod_level_nm == '5G'
        )

    if not end_date:
        end_date = start_date

    if start_date:
        stmt_sbscr = stmt_sbscr.where(between(models.Subscr.base_date, start_date, end_date))
        stmt_voc = stmt_voc.where(between(models.VocList.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt_sbscr = stmt_sbscr.where(models.Subscr.biz_hq_nm == group)
        stmt_voc = stmt_voc.where(models.VocList.biz_hq_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt_sbscr = stmt_sbscr.where(models.Subscr.oper_team_nm == group)
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm == group)

    stmt_sbscr = stmt_sbscr.group_by(models.Subscr.base_date).order_by(models.Subscr.base_date.asc()).subquery()
    stmt_voc = stmt_voc.group_by(models.VocList.base_date).order_by(models.VocList.base_date.asc()).subquery()

    stmt = select(
            stmt_sbscr.c.base_date.label("date"),
            func.nvl(func.round(stmt_voc.c.voc_cnt / stmt_sbscr.c.sbscr_cnt * 1000.0, 4), 0.0).label("value"),
            ).outerjoin(
                stmt_voc,
                (stmt_voc.c.base_date == stmt_sbscr.c.base_date)
            )
    query = db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend


def get_voc_event_by_group_date(db: Session, group: str = "", date: str = None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

    sum_cnt = func.sum(
        case((models.VocList.base_date == today, models.VocList.sr_tt_rcp_no_cnt)
             , else_=0)
    ).label("score")
    sum_cnt_ref = func.sum(
        case((models.VocList.base_date == ref_day, models.VocList.sr_tt_rcp_no_cnt)
             , else_=0)
    ).label("score_ref")

    entities = [
        #
    ]
    entities_groupby = [
        sum_cnt,
        sum_cnt_ref,
    ]

    stmt = select([*entities, *entities_groupby]
           ).where(
                and_(models.VocList.base_date.in_(in_cond),models.VocList.anals_3_prod_level_nm == '5G')
           )

    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.biz_hq_nm == group)

    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.oper_team_nm == group)

    elif group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)

    else:
        stmt = stmt.where(models.VocList.area_jo_nm == "")

    query = db.execute(stmt)
    query_result = query.first()
    # result = list(zip(*query_result))

    voc_event = schemas.VocEventOutput(
        title="품질VOC 발생건수(전일대비)",
        score=query_result[0],
        score_ref=query_result[1],
    )
    return voc_event

# def get_voc_event_by_group_date(db: Session, group: str="", date:str=None):
#     # today = datetime.today().strftime("%Y%m%d")
#     # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
#
#     today = date
#     ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
#     in_cond = [ref_day, today]
#
#     voc_cnt = func.sum(func.nvl(models.VocList.sr_tt_rcp_no_cnt, 0))
#     voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
#
#     entities = [
#         models.VocList.base_date,
#         # models.VocList.bts_oper_team_nm,
#         # models.VocList.area_jo_nm
#     ]
#     entities_groupby = [
#         voc_cnt
#     ]
#     if group.endswith("센터"):
#         select_group = models.VocList.biz_hq_nm
#
#     elif group.endswith("팀") or group.endswith("부"):
#         select_group = models.VocList.oper_team_nm
#
#     elif group.endswith("조"):
#         select_group = models.VocList.area_jo_nm
#
#     else:
#         select_group = None
#
#     if select_group:
#         entities.append(select_group)
#         stmt = select([*entities, *entities_groupby], models.VocList.base_date.in_(in_cond)). \
#             group_by(*entities).order_by(models.VocList.base_date.asc())
#         stmt = stmt.where(select_group == group)
#     else:
#         stmt = select([*entities, *entities_groupby], models.VocList.base_date.in_(in_cond)). \
#             group_by(*entities).order_by(models.VocList.base_date.asc())
#     try:
#         query = db.execute(stmt)
#         query_result = query.all()
#         result = list(zip(*query_result))
#         values = result[-1]
#         dates = result[0]
#     except:
#         return None
#
#     if len(values) == 1:
#         if today in dates:
#             score = values[0]
#             score_ref = 0
#         else:
#             score = 0
#             score_ref = values[0]
#     else:
#         score = values[1]
#         score_ref = values[0]
#
#
#     voc_event = schemas.VocEventOutput(
#         title = "품질VOC 발생건수(전일대비)",
#         score = score,
#         score_ref = score_ref,
#     )
#     return voc_event

