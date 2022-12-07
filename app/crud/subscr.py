from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta

# 5G단말별 가입자수: 조기준X
async def get_subscr_compare_by_hndset2(db: AsyncSession, code:str, group: str, start_date: str = '20220901', limit: int=10 ):
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
    stmt_total = select(literal("합계").label("hndset_pet_nm"), *entities_groupby) # 전국5g단말합계
    stmt_total = stmt_total.where(models.Subscr.anals_3_prod_level_nm == '5G')

    # 날짜
    stmt = stmt.where(models.Subscr.base_date.in_([start_date, lastweek]))
    stmt_total = stmt_total.where(models.Subscr.base_date.in_([start_date, lastweek]))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.biz_hq_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.Subscr.biz_hq_nm.in_(stmt_where))
        # stmt = stmt.where(models.Subscr.biz_hq_nm.in_(txt_l))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Subscr.oper_team_nm.in_(stmt_where))
        stmt = stmt.where(models.Subscr.biz_hq_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Subscr.oper_team_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.gun_gu_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.gun_gu_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.Subscr.gun_gu_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.gun_gu_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.gun_gu_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.Subscr.gun_gu_nm.in_(stmt_where))
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc()).limit(limit)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_hnd = await db.execute(stmt)
    query_result_hnd = query_hnd.all()
    query_keys_hnd = query_hnd.keys()
    
    query_total = await db.execute(stmt_total)
    query_result_total = query_total.fetchall()
    # query_keys_total = query_total.keys()

    query_keys = list(query_keys_hnd)

    query_result = query_result_hnd + query_result_total

    list_subscr_compare = list(map(lambda x: schemas.SubscrCompareOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare


#상품별가입자수(5g, lte, 3g, 합계)
async def get_subscr_compare_by_prod(db: AsyncSession, code: str, group: str, start_date: str = '20220901', limit: int = 10):
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
    stmt_total = select(literal("합계").label("prod"), *entities_groupby)  # 전국5g단말합계


    #날짜
    stmt = stmt.where(models.Subscr.base_date.in_([start_date, lastweek]))
    stmt_total = stmt_total.where(models.Subscr.base_date.in_([start_date, lastweek]))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.biz_hq_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.Subscr.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Subscr.oper_team_nm.in_(stmt_where))
        stmt = stmt.where(models.Subscr.biz_hq_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Subscr.oper_team_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.gun_gu_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.gun_gu_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.Subscr.gun_gu_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt = stmt.where(models.Subscr.gun_gu_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.gun_gu_nm.in_(txt_l))
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc()).limit(limit)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    query_total = await db.execute(stmt_total)
    query_result_total = query_total.fetchall()
    # query_keys_total = query_total.keys()

    query_keys = list(query_keys)

    query_result = query_result + query_result_total

    list_subscr_compare = list(map(lambda x: schemas.SubscrCompareProdOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare

