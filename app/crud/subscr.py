from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal, and_
from datetime import datetime, timedelta
from app.errors import exceptions as ex

# 5G단말별 가입자수: 조기준X
async def get_subscr_compare_by_hndset(db: AsyncSession, code:str, group: str, start_date: str = '20220901', limit: int=10 ):
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
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_hq_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_center_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.new_center_nm.in_(txt_l))
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
    elif code =="전국" or code =="전체" or code == "all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

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
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_hq_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_center_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.Subscr.new_center_nm.in_(txt_l))
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
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

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


#조 X
async def get_subscr_trend_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_date: str=None, end_date: str=None):
    sum_cnt = func.sum(func.ifnull(models.Subscr.bprod_maint_sbscr_cascnt, 0.0)).label("sum_cnt")

    entities = [
        models.Subscr.base_date.label("date"),
    ]
    entities_groupby = [
        sum_cnt
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Subscr.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.Subscr.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Subscr.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Subscr.eup_myun_dong_nm.in_(stmt_where))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건(5g, lte, 3G)
    if prod and prod != "전체":
        stmt = stmt.where(models.Subscr.anals_3_prod_level_nm == prod)

    stmt = stmt.group_by(*entities).order_by(models.Subscr.base_date.asc())
    # print(stmt_cut.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_sbscr_trend = list(map(lambda x: schemas.SubscrTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_sbscr_trend


async def get_subscr_trend_item_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                              by:str="code", start_date: str=None, end_date: str=None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 계산항목
    sum_cnt = func.sum(func.ifnull(models.Subscr.bprod_maint_sbscr_cascnt, 0.0)).label("sum_cnt")

    # where절
    ## 기간 조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Subscr.base_date, start_date, end_date))

    ## 상품 조건(5g, lte, 3g)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.Subscr.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.Subscr.anals_3_prod_level_nm
    else:
        prod_column = models.Subscr.anals_3_prod_level_nm

    ## code의 값목록 : code="제조사", group="삼성|노키아"
    if group != '':
        where_ins = group.split("|")

    ## code별 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.Subscr.mkng_cmpn_nm.in_(where_ins))
        code_column = models.Subscr.mkng_cmpn_nm
    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.Subscr.new_hq_nm.in_(where_ins))
        code_column = models.Subscr.new_hq_nm
    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터", "") for txt in where_ins]
        stmt_where_and.append(models.Subscr.new_center_nm.in_(where_ins))
        code_column = models.Subscr.new_center_nm
    elif code == "팀별":
        stmt_where_and.append(models.Subscr.oper_team_nm.in_(where_ins))
        code_column = models.Subscr.oper_team_nm
    elif code == "시도별":
        stmt_where_and.append(models.Subscr.sido_nm.in_(where_ins))
        code_column = models.Subscr.sido_nm
    elif code == "시군구별":
        stmt_where_and.append(models.Subscr.gun_gu_nm.in_(where_ins))
        code_column = models.Subscr.gun_gu_nm
    elif code == "전국" or code == "전체" or code == "all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx

    # group by
    if by == "prod":
        by_column = prod_column
    elif by == "code":
        by_column = code_column
    elif by == "all":
        by_column = literal("")
    else:
        by_column = code_column

    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.Subscr.base_date.label("date"),
        sum_cnt
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.Subscr.base_date,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.SubscrTrendOutput(**r) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.SubscrTrendItemOutput(title=code, data=t_l))
    return list_items



async def get_subscr_trend_by_group_month(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_month: str=None, end_month: str=None):
    sum_cnt = func.sum(func.ifnull(models.SubscrMM.bprod_maint_sbscr_cascnt, 0.0)).label("sum_cnt")

    entities = [
        models.SubscrMM.base_ym.label("date"),
    ]
    entities_groupby = [
        sum_cnt
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_month:
        end_month = start_month

    if start_month:
        stmt = stmt.where(between(models.SubscrMM.base_ym, start_month, end_month))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")


    # 선택 조건
    if code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt = stmt.where(models.SubscrMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.SubscrMM.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.SubscrMM.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt = stmt.where(models.SubscrMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt = stmt.where(models.SubscrMM.gun_gu_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건(5g, lte,3G )
    if prod and prod != "전체":
        stmt = stmt.where(models.SubscrMM.anals_3_prod_level_nm == prod)

    stmt = stmt.group_by(*entities).order_by(models.SubscrMM.base_ym.asc())
    # print(stmt_cut.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_sbscr_trend = list(map(lambda x: schemas.SubscrTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_sbscr_trend


async def get_subscr_trend_item_by_group_month(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  by:str="code", start_month: str=None, end_month: str=None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 계산항목
    sum_cnt = func.sum(func.ifnull(models.SubscrMM.bprod_maint_sbscr_cascnt, 0.0)).label("sum_cnt")

    # where
    ## 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    stmt_where_and.append(between(models.SubscrMM.base_ym, start_month, end_month))

    ## 상품 조건(5g, lte, 3g)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.SubscrMM.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.SubscrMM.anals_3_prod_level_nm
    else:
        prod_column = models.SubscrMM.anals_3_prod_level_nm

    ## code의 값목록 : code="제조사별", group="삼성|노키아"
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.SubscrMM.new_hq_nm.in_(where_ins))
        code_column = models.SubscrMM.new_hq_nm
    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        stmt_where_and.append(models.SubscrMM.new_center_nm.in_(where_ins))
        code_column = models.SubscrMM.new_center_nm
    elif code == "팀별":
        stmt_where_and.append(models.SubscrMM.oper_team_nm.in_(where_ins))
        code_column = models.SubscrMM.oper_team_nm
    elif code == "시도별":
        stmt_where_and.append(models.SubscrMM.sido_nm.in_(where_ins))
        code_column = models.SubscrMM.sido_nm
    elif code == "시군구별":
        stmt_where_and.append(models.SubscrMM.gun_gu_nm.in_(where_ins))
        code_column = models.SubscrMM.gun_gu_nm
    elif code == "전국" or code =="전체" or code == "all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx

    # group by
    if by == "prod":
        by_column = prod_column
    elif by == "code":
        by_column = code_column
    elif by == "all":
        by_column = literal("")
    else:
        by_column = code_column

    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.SubscrMM.base_ym.label("date"),
        sum_cnt
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.SubscrMM.base_ym,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.SubscrTrendOutput(**r) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.SubscrTrendItemOutput(title=code, data=t_l))
    return list_items