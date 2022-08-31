from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta


def get_rrc_trend_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None):
    sum_rrc_try = func.sum(func.nvl(models.Rrc.rrcattempt, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.nvl(models.Rrc.rrc_success, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prbusage), 4).label("prbusage_mean")



    entities = [
        models.Rrc.base_date.label("date"),
    ]
    entities_groupby = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Rrc.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Rrc.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Rrc.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Rrc.area_jo_nm == group)
    else :
        stmt = stmt.where(models.Rrc.area_jo_nm == group)

    stmt = stmt.group_by(*entities).order_by(models.Rrc.base_date.asc())

    query = db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_rrc_trend = list(map(lambda x: schemas.RrcTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_rrc_trend


def get_worst10_rrc_bts_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None,
                                        limit: int = 10):
    sum_rrc_try = func.sum(func.nvl(models.Rrc.rrcattempt, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.nvl(models.Rrc.rrc_success, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prbusage), 4).label("prbusage_mean")

    entities = [
        models.Rrc.equip_cd.label("equip_cd"),
        models.Rrc.equip_nm.label("equip_nm"),
        # juso,
        models.Rrc.area_center_nm.label("center"),
        models.Rrc.oper_team_nm.label("team"),
        models.Rrc.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Rrc.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Rrc.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Rrc.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Rrc.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Rrc.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(sum_rrc_try>0).order_by(rrc_rate.desc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.rrc_rate.asc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_rrc_bts = list(map(lambda x: schemas.RrcBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_rrc_bts