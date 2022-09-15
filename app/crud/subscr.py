from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


def get_subscr_compare_by_hndset2(db: Session, code:str, group: str, start_date: str = '20220901', limit: int=10 ):
    if not start_date:
        start_date = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

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

    stmt = select(*entities, *entities_groupby).where(models.Subscr.anals_3_prod_level_nm == '5G')
    stmt_total = select(literal("전국5G").label("hndset_pet_nm"), *entities_groupby) # 전국5g단말합계
    stmt_total = stmt_total.where(models.Subscr.anals_3_prod_level_nm == '5G')

    # 날짜
    stmt = stmt.where(models.Subscr.base_date.in_([start_date, lastweek]))
    stmt_total = stmt_total.where(models.Subscr.base_date.in_([start_date, lastweek]))

    # 선택 조건
    if code == "제조사":
        code_val = models.Subscr.mkng_cmpn_nm
    elif code == "센터":
        code_val = models.Subscr.biz_hq_nm
    elif code == "팀":
        code_val = models.Subscr.oper_team_nm
    elif code == "시도":
        code_val = models.Subscr.sido_nm
    elif code == "시군구":
        code_val = models.Subscr.gun_gu_nm
    elif code == "읍면동":
        code_val = models.Subscr.eup_myun_dong_nm
    else:
        code_val = None

    # code의 값목록 : 삼성|노키아
    if code_val and group:
        txt_l = group.split("|")
        stmt = stmt.where(code_val.in_(txt_l))

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


def get_subscr_compare_by_prod(db: Session, code: str, group: str, start_date: str = '20220901', limit: int = 10):
    if not start_date:
        start_date = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    lastweek = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")

    sum_cnt = func.sum(case((models.Subscr.base_date == start_date, models.Subscr.bprod_maint_sbscr_cascnt)
                            , else_=0)).label("sum_cnt")
    sum_cnt_ref = func.sum(case((models.Subscr.base_date == lastweek, models.Subscr.bprod_maint_sbscr_cascnt)
                                , else_=0)).label("sum_cnt_ref")

    entities = [
        models.Subscr.anals_3_prod_level_nm.label("prod"),
    ]
    entities_groupby = [
        sum_cnt,
        sum_cnt_ref,
    ]

    stmt = select(*entities, *entities_groupby)
    stmt_total = select(literal("전국").label("prod"), *entities_groupby)  # 전국5g단말합계

    #날짜
    stmt = stmt.where(models.Subscr.base_date.in_([start_date, lastweek]))
    stmt_total = stmt_total.where(models.Subscr.base_date.in_([start_date, lastweek]))

    # 선택 조건
    if code == "제조사":
        code_val = models.Subscr.mkng_cmpn_nm
    elif code == "센터":
        code_val = models.Subscr.biz_hq_nm
    elif code == "팀":
        code_val = models.Subscr.oper_team_nm
    elif code == "시도":
        code_val = models.Subscr.sido_nm
    elif code == "시군구":
        code_val = models.Subscr.gun_gu_nm
    elif code == "읍면동":
        code_val = models.Subscr.eup_myun_dong_nm
    else:
        code_val = None

    # code의 값목록 : 삼성|노키아
    if code_val and group:
        txt_l = group.split("|")
        stmt = stmt.where(code_val.in_(txt_l))

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc())

    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    query_total = db.execute(stmt_total)
    query_result_total = query_total.fetchall()
    # query_keys_total = query_total.keys()

    query_keys = list(query_keys)

    query_result = query_result + query_result_total

    list_subscr_compare = list(map(lambda x: schemas.SubscrCompareProdOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare

###########################################
def get_subscr_compare_by_hndset(db: Session, group: str, start_date: str = '20220710', limit: int = 10):
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
    stmt_total = select(literal("전국5G").label("hndset_pet_nm"), *entities_groupby)  # 전국5g단말합계
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

