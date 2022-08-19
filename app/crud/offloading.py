from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta

def get_worst10_offloading_jo_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    sum_5g_data = func.sum(func.nvl(models.Offloading_Bts.g5d_upld_data_qnt , 0.0) +
                           func.nvl(models.Offloading_Bts.g5d_downl_data_qnt , 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.nvl(models.Offloading_Bts.sru_usagecountdl , 0.0) +
                            func.nvl(models.Offloading_Bts.sru_usagecountul , 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.nvl(models.Offloading_Bts.g3d_upld_data_qnt , 0.0) +
                           func.nvl(models.Offloading_Bts.g3d_downl_data_qnt , 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.nvl(models.Offloading_Bts.ld_downl_data_qnt , 0.0) +
                            func.nvl(models.Offloading_Bts.ld_upld_data_qnt , 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    # juso = func.concat(models.Offloading_Bts.sido_nm+' ', models.Offloading_Bts.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading_Bts.equip_nm,
        models.Offloading_Bts.equip_cd,
        # juso,
        models.Offloading_Bts.biz_hq_nm.label("center"),
        models.Offloading_Bts.oper_team_nm.label("team"),
        models.Offloading_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
        g5_off_ratio,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading_Bts.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading_Bts.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(map(lambda x: schemas.OffloadingBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts


def get_offloading_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_5g_data = func.sum(func.nvl(models.Offloading_Bts.g5d_upld_data_qnt, 0.0) +
                           func.nvl(models.Offloading_Bts.g5d_downl_data_qnt,0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.nvl(models.Offloading_Bts.sru_usagecountdl, 0.0) +
                            func.nvl(models.Offloading_Bts.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.nvl(models.Offloading_Bts.g3d_upld_data_qnt, 0.0) +
                           func.nvl(models.Offloading_Bts.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.nvl(models.Offloading_Bts.ld_downl_data_qnt, 0.0) +
                            func.nvl(models.Offloading_Bts.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")
    
    entities = [
        models.Offloading_Bts.base_date.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio
    ]
    
    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading_Bts.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading_Bts.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)

    stmt = stmt.group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())

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

    sum_5g_data = func.sum(func.nvl(models.Offloading_Bts.g5d_upld_data_qnt, 0.0) +
                           func.nvl(models.Offloading_Bts.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.nvl(models.Offloading_Bts.sru_usagecountdl, 0.0) +
                            func.nvl(models.Offloading_Bts.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.nvl(models.Offloading_Bts.g3d_upld_data_qnt, 0.0) +
                           func.nvl(models.Offloading_Bts.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.nvl(models.Offloading_Bts.ld_downl_data_qnt, 0.0) +
                            func.nvl(models.Offloading_Bts.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")

    entities = [
        models.Offloading_Bts.base_date,
        # models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        g5_off_ratio
    ]

    if group.endswith("센터"):
        select_group = models.Offloading_Bts.biz_hq_nm
    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.Offloading_Bts.oper_team_nm
    elif group.endswith("조"):
        select_group = models.Offloading_Bts.area_jo_nm
    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.Offloading_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.Offloading_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())
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


def get_worst10_offloading_hndset_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None,
                                            limit: int = 10):
    sum_5g_data = func.sum(func.nvl(models.Offloading_Hndset.g5d_upld_data_qnt, 0.0) +
                func.nvl(models.Offloading_Hndset.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum( func.nvl(models.Offloading_Hndset.sru_usagecountdl, 0.0) +
                 func.nvl(models.Offloading_Hndset.sru_usagecountul,0.0)).label("sum_sru_data")
    sum_3g_data = func.sum( func.nvl(models.Offloading_Hndset.g3d_upld_data_qnt, 0.0) +
                 func.nvl(models.Offloading_Hndset.g3d_downl_data_qnt,0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.nvl(models.Offloading_Hndset.ld_downl_data_qnt, 0.0) +
                 func.nvl(models.Offloading_Hndset.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading_Hndset.sido_nm + ' ', models.Offloading_Hndset.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading_Hndset.hndset_pet_nm,
    ]
    entities_groupby = [
        g5_off_ratio
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading_Hndset.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading_Hndset.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm == group)
    else:
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm == group)

    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(
        map(lambda x: schemas.OffloadingHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts

# def get_offloading_compare_by_group_date(db: Session, group: str, date:str=None):
#     sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
#     sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
#     sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
#     g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
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