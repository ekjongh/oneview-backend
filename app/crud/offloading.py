from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta

def get_worst10_offloading_jo_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.nvl(models.Offloading.g3_total_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.nvl(models.Offloading.gl_total_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0)).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading.sido_nm, models.Offloading.eup_myun_dong_nm).label("juso")

    entities = [
        # models.Offloading.equip_nm.label("기지국명"),
        # models.Offloading.equip_cd.label("equip_cd"),
        juso,
        models.Offloading.area_center_nm.label("center"),
        models.Offloading.oper_team_nm.label("team"),
        models.Offloading.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        group = group[:-2]
        stmt = stmt.where(models.Offloading.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Offloading.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc())
    
    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(map(lambda x: schemas.OffloadingBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts


def get_offloading_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")
    
    entities = [
        models.Offloading.base_date.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio
    ]
    
    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        group = group[:-2]
        stmt = stmt.where(models.Offloading.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Offloading.area_jo_nm == group)
    
    stmt = stmt.group_by(*entities).order_by(models.Offloading.base_date.asc())

    query = db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_trend

def get_offloading_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + sum_sru_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")

    entities = [
        models.Offloading.base_date,
        # models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        g5_off_ratio
    ]

    if group.endswith("센터"):
        select_group = models.Offloading.area_center_nm
        print(group)
        group = group[:-2]

    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.Offloading.oper_team_nm

    elif group.endswith("조"):
        select_group = models.Offloading.area_jo_nm

    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.Offloading.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.Offloading.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading.base_date.asc())
    try:
        query = db.execute(stmt)
        query_result = query.all()
        query_keys = query.keys()
        result = list(zip(*query_result))
        values = result[-1]
        dates = result[0]
    except:
        return None
    print("date: ", in_cond)
    print("resut: ", result)
    print("keys: ", query_keys)
    print(dict(zip(query_keys, result)))


    if len(values) == 1:
        if today in dates:
            score = values[0]
            score_ref = 0
        else:
            score = 0
            score_ref = values[0]
    else:
        score = values[1]
        score_ref = values[0]

    offloading_event = schemas.OffloadingEventOutput(
        title = "5G 오프로딩 (전일대비)",
        score = score,
        score_ref = score_ref,
    )
    return offloading_event


# def get_offloading_compare_by_group_date(db: Session, group: str, date:str=None):
#     sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
#     sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
#     sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
#     g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + sum_sru_data + 1e-6) * 100
#     g5_off_ratio = func.round(g5_off_ratio, 4)
#     g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
#
#     entities = [
#         models.Offloading.base_date,
#         models.Offloading.area_jo_nm
#     ]
#     entities_groupby = [
#         g5_off_ratio
#     ]
#     stmt = select(*entities, *entities_groupby)
#
#     if not date:
#         date = datetime.today().strftime("%Y%m%d")
#         yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
#
#     stmt = stmt.where(between(models.Offloading.base_date, yesterday, date))
#
#     if group.endswith("팀") or group.endswith("부"):
#         stmt = stmt.where(models.Offloading.bts_oper_team_nm == group)
#
#
#     stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc())
#     # query_result = db.execute(stmt).all()
#     pass