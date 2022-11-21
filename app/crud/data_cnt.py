from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


async def get_datacnt_trend_by_group_date2(db: AsyncSession, code: str, group: str, start_date: str = None,
                                              end_date: str = None):
    sum_5g_data = (func.ifnull(models.DataCnt.g5d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_3g_data = (func.ifnull(models.DataCnt.g3d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = (func.ifnull(models.DataCnt.ld_downl_data_qnt, 0.0) +
                    func.ifnull(models.DataCnt.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("value")


    entities = [
        models.DataCnt.base_date.label("date"),
    ]
    entities_groupby = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_total_data
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.DataCnt.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.DataCnt.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.DataCnt.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.DataCnt.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(txt_l))
    else:  # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(models.DataCnt.base_date.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    result = list(map(lambda x: schemas.DataCntTrendOutput(**dict(zip(query_keys, x))), query_result))
    return result


async def get_datacnt_compare_by_prod(db: AsyncSession, code: str, group: str, start_date: str = '20220901', limit: int = 10):
    if not start_date:
        start_date = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    lastweek = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")

    sum_5g_data = (func.ifnull(models.DataCnt.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.DataCnt.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_3g_data = (func.ifnull(models.DataCnt.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.DataCnt.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = (func.ifnull(models.DataCnt.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.DataCnt.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
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

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.DataCnt.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.DataCnt.oper_team_nm.in_(stmt_where))
        stmt = stmt.where(models.DataCnt.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.DataCnt.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc())

    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    query_keys = list(query_keys)

    list_subscr_compare = list(map(lambda x: schemas.DataCntCompareProdOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare

