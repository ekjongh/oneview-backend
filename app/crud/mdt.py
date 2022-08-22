from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta


def get_mdt_trend_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None):
    sum_rsrp_m105d_cnt = func.sum(func.nvl(models.Mdt.rsrp_m105d_cnt, 0.0))
    sum_rsrp_m110d_cnt = func.sum(func.nvl(models.Mdt.rsrp_m110d_cnt, 0.0))
    sum_rsrp_cnt = func.sum(func.nvl(models.Mdt.rsrp_cnt, 0.0))
    sum_rsrp_value = func.sum(func.nvl(models.Mdt.rsrp_sum, 0.0))

    sum_rsrq_m15d_cnt = func.sum(func.nvl(models.Mdt.rsrq_m15d_cnt, 0.0))
    sum_rsrq_m17d_cnt = func.sum(func.nvl(models.Mdt.rsrq_m17d_cnt, 0.0))
    sum_rsrq_cnt = func.sum(func.nvl(models.Mdt.rsrq_cnt, 0.0))
    sum_rsrq_value = func.sum(func.nvl(models.Mdt.rsrq_sum, 0.0))

    sum_rip_maxd_cnt = func.sum(func.nvl(models.Mdt.new_rip_maxd_cnt, 0.0))
    sum_rip_cnt = func.sum(func.nvl(models.Mdt.rip_cnt, 0.0))
    sum_rip_value = func.sum(func.nvl(models.Mdt.rip_sum, 0.0))

    sum_new_phr_m3d_cnt = func.sum(func.nvl(models.Mdt.new_phr_m3d_cnt , 0.0))
    sum_new_phr_mind_cnt_cnt = func.sum(func.nvl(models.Mdt.new_phr_mind_cnt, 0.0))
    sum_phr_cnt = func.sum(func.nvl(models.Mdt.phr_cnt, 0.0))
    sum_phr_value = func.sum(func.nvl(models.Mdt.phr_sum, 0.0))

    sum_nr_rsrp_cnt = func.sum(func.nvl(models.Mdt.nr_rsrp_cnt, 0.0))
    sum_nr_rsrp_value = func.sum(func.nvl(models.Mdt.nr_rsrp_sum, 0.0))

    rsrp_bad_rate = (sum_rsrp_m105d_cnt + sum_rsrp_m110d_cnt) / (sum_rsrp_cnt + 1e-6) * 100
    rsrp_bad_rate = func.round(rsrp_bad_rate, 4)
    rsrp_bad_rate = func.coalesce(rsrp_bad_rate, 0.0).label("rsrp_bad_rate")
    rsrp_mean = (sum_rsrp_value / (sum_rsrp_cnt + 1e-6))
    rsrp_mean = func.round(rsrp_mean, 4)
    rsrp_mean = func.coalesce(rsrp_mean, 0.0).label("rsrp_mean")

    rsrq_bad_rate = (sum_rsrq_m15d_cnt + sum_rsrq_m17d_cnt) / (sum_rsrq_cnt + 1e-6) * 100
    rsrq_bad_rate = func.round(rsrq_bad_rate, 4)
    rsrq_bad_rate = func.coalesce(rsrq_bad_rate, 0.0).label("rsrq_bad_rate")
    rsrq_mean = (sum_rsrq_value / (sum_rsrq_cnt + 1e-6))
    rsrq_mean = func.round(rsrq_mean, 4)
    rsrq_mean = func.coalesce(rsrq_mean, 0.0).label("rsrq_mean")

    rip_bad_rate = (sum_rip_maxd_cnt) / (sum_rip_cnt + 1e-6) * 100
    rip_bad_rate = func.round(rip_bad_rate, 4)
    rip_bad_rate = func.coalesce(rip_bad_rate, 0.0).label("rip_bad_rate")
    rip_mean = (sum_rip_value / (sum_rip_cnt + 1e-6))
    rip_mean = func.round(rip_mean, 4)
    rip_mean = func.coalesce(rip_mean, 0.0).label("rip_mean")

    phr_bad_rate = (sum_new_phr_m3d_cnt + sum_new_phr_mind_cnt_cnt) / (sum_phr_cnt + 1e-6) * 100
    phr_bad_rate = func.round(rsrq_bad_rate, 4)
    phr_bad_rate = func.coalesce(rsrq_bad_rate, 0.0).label("phr_bad_rate")
    phr_mean = (sum_phr_value / (sum_phr_cnt + 1e-6))
    phr_mean = func.round(phr_mean, 4)
    phr_mean = func.coalesce(phr_mean, 0.0).label("phr_mean")

    nr_rsrp_mean = (sum_nr_rsrp_value / (sum_nr_rsrp_cnt + 1e-6))
    nr_rsrp_mean = func.round(nr_rsrp_mean, 4)
    nr_rsrp_mean = func.coalesce(nr_rsrp_mean, 0.0).label("nr_rsrp_mean")

    entities = [
        models.Mdt.base_date.label("date"),
    ]
    entities_groupby = [
        rsrp_bad_rate,
        rsrp_mean,
        rsrq_bad_rate,
        rsrq_mean,
        rip_bad_rate,
        rip_mean,
        phr_bad_rate,
        phr_mean,
        nr_rsrp_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Mdt.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Mdt.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Mdt.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Mdt.area_jo_nm == group)
    else :
        stmt = stmt.where(models.Mdt.area_jo_nm == group)

    stmt = stmt.group_by(*entities).order_by(models.Mdt.base_date.asc())

    query = db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_mdt_trend = list(map(lambda x: schemas.MdtTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_mdt_trend


def get_worst10_mdt_bts_by_group_date(db: Session, group: str, start_date: str = None, end_date: str = None,
                                        limit: int = 10):
    sum_rsrp_m105d_cnt = func.sum(func.nvl(models.Mdt.rsrp_m105d_cnt, 0.0))
    sum_rsrp_m110d_cnt = func.sum(func.nvl(models.Mdt.rsrp_m110d_cnt, 0.0))
    sum_rsrp_cnt = func.sum(func.nvl(models.Mdt.rsrp_cnt, 0.0))
    sum_rsrp_value = func.sum(func.nvl(models.Mdt.rsrp_sum, 0.0))

    sum_rsrq_m15d_cnt = func.sum(func.nvl(models.Mdt.rsrq_m15d_cnt, 0.0))
    sum_rsrq_m17d_cnt = func.sum(func.nvl(models.Mdt.rsrq_m17d_cnt, 0.0))
    sum_rsrq_cnt = func.sum(func.nvl(models.Mdt.rsrq_cnt, 0.0))
    sum_rsrq_value = func.sum(func.nvl(models.Mdt.rsrq_sum, 0.0))

    sum_rip_maxd_cnt = func.sum(func.nvl(models.Mdt.new_rip_maxd_cnt, 0.0))
    sum_rip_cnt = func.sum(func.nvl(models.Mdt.rip_cnt, 0.0))
    sum_rip_value = func.sum(func.nvl(models.Mdt.rip_sum, 0.0))

    sum_new_phr_m3d_cnt = func.sum(func.nvl(models.Mdt.new_phr_m3d_cnt , 0.0))
    sum_new_phr_mind_cnt_cnt = func.sum(func.nvl(models.Mdt.new_phr_mind_cnt, 0.0))
    sum_phr_cnt = func.sum(func.nvl(models.Mdt.phr_cnt, 0.0))
    sum_phr_value = func.sum(func.nvl(models.Mdt.phr_sum, 0.0))

    sum_nr_rsrp_cnt = func.sum(func.nvl(models.Mdt.nr_rsrp_cnt, 0.0))
    sum_nr_rsrp_value = func.sum(func.nvl(models.Mdt.nr_rsrp_sum, 0.0))

    rsrp_bad_rate = (sum_rsrp_m105d_cnt + sum_rsrp_m110d_cnt) / (sum_rsrp_cnt + 1e-6) * 100
    rsrp_bad_rate = func.round(rsrp_bad_rate, 4)
    rsrp_bad_rate = func.coalesce(rsrp_bad_rate, 0.0).label("rsrp_bad_rate")
    rsrp_mean = (sum_rsrp_value / (sum_rsrp_cnt + 1e-6))
    rsrp_mean = func.round(rsrp_mean, 4)
    rsrp_mean = func.coalesce(rsrp_mean, 0.0).label("rsrp_mean")

    rsrq_bad_rate = (sum_rsrq_m15d_cnt + sum_rsrq_m17d_cnt) / (sum_rsrq_cnt + 1e-6) * 100
    rsrq_bad_rate = func.round(rsrq_bad_rate, 4)
    rsrq_bad_rate = func.coalesce(rsrq_bad_rate, 0.0).label("rsrq_bad_rate")
    rsrq_mean = (sum_rsrq_value / (sum_rsrq_cnt + 1e-6))
    rsrq_mean = func.round(rsrq_mean, 4)
    rsrq_mean = func.coalesce(rsrq_mean, 0.0).label("rsrq_mean")

    rip_bad_rate = (sum_rip_maxd_cnt) / (sum_rip_cnt + 1e-6) * 100
    rip_bad_rate = func.round(rip_bad_rate, 4)
    rip_bad_rate = func.coalesce(rip_bad_rate, 0.0).label("rip_bad_rate")
    rip_mean = (sum_rip_value / (sum_rip_cnt + 1e-6))
    rip_mean = func.round(rip_mean, 4)
    rip_mean = func.coalesce(rip_mean, 0.0).label("rip_mean")

    phr_bad_rate = (sum_new_phr_m3d_cnt + sum_new_phr_mind_cnt_cnt) / (sum_phr_cnt + 1e-6) * 100
    phr_bad_rate = func.round(rsrq_bad_rate, 4)
    phr_bad_rate = func.coalesce(rsrq_bad_rate, 0.0).label("phr_bad_rate")
    phr_mean = (sum_phr_value / (sum_phr_cnt + 1e-6))
    phr_mean = func.round(phr_mean, 4)
    phr_mean = func.coalesce(phr_mean, 0.0).label("phr_mean")

    nr_rsrp_mean = (sum_nr_rsrp_value / (sum_nr_rsrp_cnt + 1e-6))
    nr_rsrp_mean = func.round(nr_rsrp_mean, 4)
    nr_rsrp_mean = func.coalesce(nr_rsrp_mean, 0.0).label("nr_rsrp_mean")

    # juso = func.concat(models.Mdt.sido_nm+' ', models.Mdt.eup_myun_dong_nm).label("juso")

    entities = [
        models.Mdt.equip_cd.label("equip_cd"),
        models.Mdt.equip_nm.label("equip_nm"),
        # juso,
        models.Mdt.area_center_nm.label("center"),
        models.Mdt.oper_team_nm.label("team"),
        models.Mdt.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        rsrp_bad_rate,
        rsrq_bad_rate,
        rip_bad_rate,
        phr_bad_rate,
        nr_rsrp_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Mdt.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Mdt.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Mdt.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Mdt.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Mdt.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(sum_rsrp_cnt > 0).order_by(rsrp_bad_rate.desc()).subquery()

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.rsrp_bad_rate.desc()).label("RANK"),
        *stmt.c
    ])

    query = db.execute(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_mdt_bts = list(map(lambda x: schemas.MdtBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_mdt_bts