from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case, literal, and_
from datetime import datetime, timedelta
from app.errors import exceptions as ex


#조기준 X
async def get_datacnt_trend_by_group_date(db: AsyncSession, prod:str, code: str, group: str, start_date: str = None,
                                              end_date: str = None):
    sum_5g_data = func.sum(func.ifnull(models.DataCnt.g5d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_3g_data = func.sum(func.ifnull(models.DataCnt.g3d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.DataCnt.ld_downl_data_qnt, 0.0) +
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

    # 상품 조건(5g, lte, 3g)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt = stmt.where(models.DataCnt.anals_3_prod_level_nm.in_(prod_l))

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.DataCnt.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.DataCnt.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.DataCnt.new_center_nm.in_(txt_l))
    elif code == "팀별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.DataCnt.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(models.DataCnt.base_date.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    result = list(map(lambda x: schemas.DataCntTrendOutput(**dict(zip(query_keys, x))), query_result))
    return result


#조기준 X
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
    stmt_total = select(literal("합계").label("prod"), *entities_groupby)

    #날짜
    stmt = stmt.where(models.DataCnt.base_date.in_([start_date, lastweek]))
    stmt_total = stmt_total.where(models.DataCnt.base_date.in_([start_date, lastweek]))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.DataCnt.mkng_cmpn_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.DataCnt.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.DataCnt.new_hq_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.DataCnt.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.DataCnt.new_center_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.DataCnt.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.DataCnt.oper_team_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.DataCnt.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
        stmt_total = stmt_total.where(models.DataCnt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.DataCnt.eup_myun_dong_nm.in_(txt_l))
        stmt_total = stmt_total.where(models.DataCnt.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code == "전체" or code == "all":
        pass
    else: 
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.where(models.DataCnt.anals_3_prod_level_nm!="MVNO")
    stmt = stmt.group_by(*entities).order_by(sum_cnt.desc())
    stmt_total = stmt_total.where(models.DataCnt.anals_3_prod_level_nm != "MVNO")
    stmt_total = stmt_total.order_by(sum_cnt.desc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()
    query_keys = list(query_keys)

    #합계 query 실행
    query_total = await db.execute(stmt_total)
    query_result_total = query_total.fetchall()

    query_result = query_result + query_result_total

    list_subscr_compare = list(map(lambda x: schemas.DataCntCompareProdOutput(**dict(zip(query_keys, x))), query_result))
    return list_subscr_compare


async def get_datacnt_trend_item_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  by:str="code", start_date: str=None, end_date: str=None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 계산항목
    sum_5g_data = (func.ifnull(models.DataCnt.g5d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_3g_data = (func.ifnull(models.DataCnt.g3d_upld_data_qnt, 0.0) +
                   func.ifnull(models.DataCnt.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = (func.ifnull(models.DataCnt.ld_downl_data_qnt, 0.0) +
                    func.ifnull(models.DataCnt.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = func.sum(sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")

    sum_cnt = sum_total_data.label("value")

    # where 
    ## 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.DataCnt.base_date, start_date, end_date))

    ## 상품 조건(5g, lte, 3g)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.DataCnt.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.DataCnt.anals_3_prod_level_nm
    else:
        prod_column = models.DataCnt.anals_3_prod_level_nm

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.DataCnt.mkng_cmpn_nm.in_(where_ins))
        code_column = models.DataCnt.mkng_cmpn_nm
    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.DataCnt.new_hq_nm.in_(where_ins))
        code_column = models.DataCnt.new_hq_nm
    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터", "") for txt in where_ins]
        stmt_where_and.append(models.DataCnt.new_center_nm.in_(where_ins))
        code_column = models.DataCnt.new_center_nm
    elif code == "팀별":
        stmt_where_and.append(models.DataCnt.oper_team_nm.in_(where_ins))
        code_column = models.DataCnt.oper_team_nm
    elif code == "시도별":
        stmt_where_and.append(models.DataCnt.sido_nm.in_(where_ins))
        code_column = models.DataCnt.sido_nm
    elif code == "시군구별":
        stmt_where_and.append(models.DataCnt.gun_gu_nm.in_(where_ins))
        code_column = models.DataCnt.gun_gu_nm
    elif code == "읍면동별":
        stmt_where_and.append(models.DataCnt.eup_myun_dong_nm.in_(where_ins))
        code_column = models.DataCnt.eup_myun_dong_nm
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
        models.DataCnt.base_date.label("date"),
        sum_cnt
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.DataCnt.base_date,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.DataCntTrendOutput(**r) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.DataCntTrendItemOutput(title=code, data=t_l))
    return list_items