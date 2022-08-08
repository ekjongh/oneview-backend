from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta


def get_worst10_volte_bts_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    # get_worst10_volte_bts_by_group_date(db: Session, group: str = None, start_date: str=None, end_date: str=None, limit: int=10):
    sum_try = func.sum(func.nvl(models.Volte.wjxbfs1, 0.0)).label("sum_try")
    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0)).label("sum_suc")
    sum_fail = func.sum(func.nvl(models.Volte.wjxbfs3, 0.0)).label("sum_fail")
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.Volte.sido_nm, models.Volte.eup_myun_dong_nm).label("juso")

    entities = [
        models.Volte.equip_nm.label("기지국명"),
        juso,
        # models.Volte.area_hq_nm,
        models.Volte.area_center_nm.label("center"),
        models.Volte.oper_team_nm.label("team"),
        models.Volte.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        sum_fail,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Volte.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        group = group[:-2]
        stmt = stmt.where(models.Volte.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Volte.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Volte.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(sum_try>100).order_by(cut_ratio.desc())

    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_bts


def get_volte_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    entities_cut = [
        models.Volte.base_date.label("date"),
    ]
    entities_groupby_cut = [
        cut_ratio
    ]

    stmt_cut = select(*entities_cut, *entities_groupby_cut)

    fc_373_cnt = func.sum(case([(models.VolteFc.fc == '373', func.nvl(models.VolteFc.wjxbfs1, 0.0))])).label("fc_373")
    fc_9563_cnt = func.sum(case([(models.VolteFc.fc == '9563', func.nvl(models.VolteFc.wjxbfs1, 0.0))])).label("fc_9563")

    entities_fc = [
        models.VolteFc.base_date
    ]
    entities_groupby_fc = [
        fc_373_cnt,
        fc_9563_cnt,
    ]

    stmt_fc = select(*entities_fc, *entities_groupby_fc)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt_cut = stmt_cut.where(between(models.Volte.base_date, start_date, end_date))
        stmt_fc = stmt_fc.where(between(models.VolteFc.base_date, start_date, end_date))

    if group.endswith("센터"):
        group = group[:-2]
        stmt_cut = stmt_cut.where(models.Volte.area_center_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt_cut = stmt_cut.where(models.Volte.oper_team_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.oper_team_nm == group)

    if group.endswith("조"):
        stmt_cut = stmt_cut.where(models.Volte.area_jo_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.area_jo_nm == group)

    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.Volte.base_date.asc())
    stmt_fc = stmt_fc.group_by(*entities_fc).order_by(models.VolteFc.base_date.asc())

    query_cut = db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    query_fc = db.execute(stmt_fc)
    query_result_fc = query_fc.all()
    query_keys_fc = query_fc.keys()

    query_keys = list(query_keys_cut) + list(query_keys_fc)[1:]

    query_result = list(map(lambda result1, result2: list(result1) + list(result2[1:]),\
                            query_result_cut, query_result_fc))

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_volte_trend


def get_volte_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.Volte.base_date,
        # models.Volte.area_jo_nm
    ]
    entities_groupby = [
        cut_ratio
    ]

    if group.endswith("센터"):
        select_group = models.Volte.area_center_nm
        group = group[:-2]

    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.Volte.oper_team_nm

    elif group.endswith("조"):
        select_group = models.Volte.area_jo_nm

    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.Volte.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Volte.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.Volte.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Volte.base_date.asc())
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

    volte_event = schemas.VolteEventOutput(
        title = "VoLTE 절단율(전일대비)",
        score = score,
        score_ref = score_ref,
    )
    return volte_event
