from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


def get_subscr_compare_by_hndset(db: Session, group: str, start_date: str = '20220710', limit: int=10 ):
    thisweek_end = start_date
    thisweek_start = (datetime.strptime(thisweek_end, "%Y%m%d") - timedelta(6)).strftime("%Y%m%d")
    lastweek_end =  (datetime.strptime(thisweek_end, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")
    lastweek_start = (datetime.strptime(thisweek_end, "%Y%m%d") - timedelta(13)).strftime("%Y%m%d")

    sum_cnt  = func.sum(case(
                            (between(models.Subscr.base_date, thisweek_start, thisweek_end),
                                models.Subscr.bprod_maint_sbscr_cascnt)
                        ,else_=0)).label("금주")
    sum_cnt_ref  = func.sum(case(
                            (between(models.Subscr.base_date, lastweek_start, lastweek_end),
                                models.Subscr.bprod_maint_sbscr_cascnt)
                        ,else_=0)).label("전주")

    entities = [
        models.Subscr.hndset_pet_nm.label("단말명"),
    ]
    entities_groupby = [
        sum_cnt,
        sum_cnt_ref,
    ]

    stmt = select(*entities, *entities_groupby)
    stmt_total = select(literal("total").label("단말명"), *entities_groupby) #전국단말합계

    if start_date:
        stmt = stmt.where(between(models.Subscr.base_date, lastweek_start, thisweek_end))
        stmt_total = stmt_total.where(between(models.Subscr.base_date, lastweek_start, thisweek_end))

    if group.endswith("센터"):
        group = group[:-2]
        stmt = stmt.where(models.Subscr.biz_hq_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Subscr.oper_team_nm == group)

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc())

    query_hnd = db.execute(stmt)
    query_result_hnd = query_hnd.fetchmany(size=limit)
    query_keys_hnd = query_hnd.keys()
    
    query_total = db.execute(stmt_total)
    query_result_total = query_total.fetchall()
    # query_keys_total = query_total.keys()

    query_keys = list(query_keys_hnd)

    query_result = query_result_hnd + query_result_total

    list_subscr_compare = list(map(lambda x: schemas.SubscrCompareOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare


