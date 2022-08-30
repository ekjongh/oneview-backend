from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta


def get_worst10_volte_bts_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    # 5G VOLTE 절단율 worst 10 기지국
    # get_worst10_volte_bts_by_group_date(db: Session, group: str = None, start_date: str=None, end_date: str=None, limit: int=10):
    sum_try = func.sum(func.nvl(models.Volte_Fail_Bts.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.nvl(models.Volte_Fail_Bts.comp_cacnt, 0.0)).label("sum_suc")
    # sum_fail = func.sum(func.nvl(models.Volte_Fail_Bts.fail_cacnt, 0.0)).label("sum_fail")
    sum_cut = func.sum(func.nvl(models.Volte_Fail_Bts.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.Volte_Fail_Bts.sido_nm+' ', models.Volte_Fail_Bts.eup_myun_dong_nm).label("juso")

    entities = [
        models.Volte_Fail_Bts.equip_nm,
        models.Volte_Fail_Bts.equip_cd,
        # juso,
        models.Volte_Fail_Bts.biz_hq_nm.label("center"),
        models.Volte_Fail_Bts.oper_team_nm.label("team"),
        models.Volte_Fail_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        # sum_fail,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby).where(models.Volte_Fail_Bts.anals_3_prod_level_nm=='5G')

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Volte_Fail_Bts.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.Volte_Fail_Bts.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Volte_Fail_Bts.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Volte_Fail_Bts.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Volte_Fail_Bts.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(sum_try>100).order_by(cut_ratio.desc()).subquery()
    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])
    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_bts


def get_worst10_volte_hndset_by_group_date(db: Session, group: str, start_date: str = None, end_date: str=None, limit: int = 10):
    # 5G VOLTE 절단율 worst 10 단말기
    sum_try = func.sum(func.nvl(models.Volte_Fail_Hndset.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.nvl(models.Volte_Fail_Hndset.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.nvl(models.Volte_Fail_Hndset.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.Volte_Fail_Hndset.hndset_pet_nm,
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby).where(models.Volte_Fail_Hndset.anals_3_prod_level_nm=='5G')

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Volte_Fail_Hndset.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Volte_Fail_Hndset.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Volte_Fail_Hndset.oper_team_nm == group)
    else:
        stmt = stmt.where(models.Volte_Fail_Hndset.oper_team_nm == group)

    stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(cut_ratio.desc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    print(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_volte_hndset = list(map(lambda x: schemas.VolteHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_hndset



def get_volte_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_suc = func.sum(func.nvl(models.Volte_Fail_Bts.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.nvl(models.Volte_Fail_Bts.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    fc_373_cnt = func.sum(func.nvl(models.Volte_Fail_Bts.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.nvl(models.Volte_Fail_Bts.fc9563_cnt, 0.0)).label("fc_9563")

    entities_cut = [
        models.Volte_Fail_Bts.base_date.label("date"),
    ]
    entities_groupby_cut = [
        cut_ratio,
        fc_373_cnt,
        fc_9563_cnt
    ]

    stmt_cut = select(*entities_cut, *entities_groupby_cut).where(models.Volte_Fail_Bts.anals_3_prod_level_nm=='5G')

    if not end_date:
        end_date = start_date

    if start_date:
        stmt_cut = stmt_cut.where(between(models.Volte_Fail_Bts.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt_cut = stmt_cut.where(models.Volte_Fail_Bts.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt_cut = stmt_cut.where(models.Volte_Fail_Bts.oper_team_nm == group)
    elif group.endswith("조"):
        stmt_cut = stmt_cut.where(models.Volte_Fail_Bts.area_jo_nm == group)
    else:
        stmt_cut = stmt_cut.where(models.Volte_Fail_Bts.area_jo_nm == group)

    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.Volte_Fail_Bts.base_date.asc())

    query_cut = db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys_cut, x))), query_result_cut))
    return list_volte_trend


def get_volte_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

    sum_suc = func.sum(func.nvl(models.Volte_Fail_Bts.comp_cacnt, 0.0))
    sum_cut = func.sum(func.nvl(models.Volte_Fail_Bts.fail_cacnt, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.Volte_Fail_Bts.base_date,
        # models.Volte_Fail_Bts.area_jo_nm
    ]
    entities_groupby = [
        cut_ratio
    ]

    if group.endswith("센터"):
        select_group = models.Volte_Fail_Bts.biz_hq_nm
    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.Volte_Fail_Bts.oper_team_nm
    elif group.endswith("조"):
        select_group = models.Volte_Fail_Bts.area_jo_nm
    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.Volte_Fail_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Volte_Fail_Bts.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.Volte_Fail_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Volte_Fail_Bts.base_date.asc())
    try:
        query = db.execute(stmt)
        query_result = query.all()
        query_keys = query.keys()
        result = list(zip(*query_result))
        values = result[-1]
        dates = result[0]
    except:
        return None
    # print("date: ", in_cond)
    # print("resut: ", result)
    # print("keys: ", query_keys)
    # print(dict(zip(query_keys, result)))

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