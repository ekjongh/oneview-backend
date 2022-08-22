from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


def get_subscr_compare_by_hndset(db: Session, group: str, start_date: str = '20220710', limit: int=10 ):
    lastweek = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")

    sum_cnt = func.sum(case((models.Subscr.base_date == start_date, models.Subscr.bprod_maint_sbscr_cascnt)
                        , else_=0)).label("sum_cnt")
    sum_cnt_ref = func.sum(case((models.Subscr.base_date == lastweek, models.Subscr.bprod_maint_sbscr_cascnt)
                        , else_=0)).label("sum_cnt_ref")

    entities = [
        models.Subscr.hndset_pet_nm,
    ]
    entities_groupby = [
        sum_cnt,
        sum_cnt_ref,
    ]

    stmt = select(*entities, *entities_groupby)
    stmt_total = select(literal("전국5G").label("hndset_pet_nm"), *entities_groupby) # 전국5g단말합계
    stmt_total = stmt_total.where(models.Subscr.anals_3_prod_level_nm == '5G')

    if start_date:
        stmt = stmt.where(models.Subscr.base_date.in_([start_date, lastweek]))
        stmt_total = stmt_total.where(models.Subscr.base_date.in_([start_date, lastweek]))

    if group.endswith("센터"):
        stmt = stmt.where(models.Subscr.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Subscr.oper_team_nm == group)
    else:
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


