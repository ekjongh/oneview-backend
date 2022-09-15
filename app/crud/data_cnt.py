from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta



def get_datacnt_compare_by_prod(db: Session, code: str, group: str, start_date: str = '20220901', limit: int = 10):
    if not start_date:
        start_date = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    lastweek = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")

    sum_5g_data = (func.nvl(models.DataCnt.g5d_upld_data_qnt, 0.0) +
                           func.nvl(models.DataCnt.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_3g_data = (func.nvl(models.DataCnt.g3d_upld_data_qnt, 0.0) +
                           func.nvl(models.DataCnt.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = (func.nvl(models.DataCnt.ld_downl_data_qnt, 0.0) +
                            func.nvl(models.DataCnt.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")


    sum_cnt = func.sum(case((models.DataCnt.base_date == start_date, sum_total_data)
                            , else_=0)).label("sum_cnt")
    sum_cnt_ref = func.sum(case((models.DataCnt.base_date == lastweek, sum_total_data)
                                , else_=0)).label("sum_cnt_ref")

    entities = [
        models.DataCnt.anals_3_prod_level_nm.label("prod"),
    ]
    entities_groupby = [
        sum_cnt,
        sum_cnt_ref,
    ]

    stmt = select(*entities, *entities_groupby)

    #날짜
    stmt = stmt.where(models.DataCnt.base_date.in_([start_date, lastweek]))

    # 선택 조건
    if code == "제조사":
        code_val = models.DataCnt.mkng_cmpn_nm
    elif code == "센터":
        code_val = models.DataCnt.biz_hq_nm
    elif code == "팀":
        code_val = models.DataCnt.oper_team_nm
    elif code == "시도":
        code_val = models.DataCnt.sido_nm
    elif code == "시군구":
        code_val = models.DataCnt.gun_gu_nm
    elif code == "읍면동":
        code_val = models.DataCnt.eup_myun_dong_nm
    else:
        code_val = None

    # code의 값목록 : 삼성|노키아
    if code_val and group:
        txt_l = group.split("|")
        stmt = stmt.where(code_val.in_(txt_l))

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc())
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    query_keys = list(query_keys)

    list_subscr_compare = list(map(lambda x: schemas.DataCntCompareProdOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare

