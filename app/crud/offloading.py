from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_, or_, literal
from datetime import datetime, timedelta


def date_range(start, end):
    start = datetime.strptime(start, '%Y%m%d')
    end = datetime.strptime(end, '%Y%m%d')
    dates = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end - start).days + 1)]
    return dates


def make_case_code(query_result):
    # query result : [(bonbu, center),()]
    case_dict = {}
    suborg_list = []
    for r in query_result:
        suborg_list.append(r[1])
        if r[0] in case_dict:
            case_dict[r[0]].append(r[1])
        else:
            case_dict[r[0]] = [r[1]]

    return case_dict, suborg_list


async def get_offloading_trend_by_group_date(db: AsyncSession, code: str, group: str, start_date: str = None,
                                              end_date: str = None):
    # 집계항목
    sum_5g_data = func.sum(func.ifnull(models.Offloading.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.Offloading.sru_usagecountdl, 0.0) +
                            func.ifnull(models.Offloading.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.Offloading.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.Offloading.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.Offloading.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")

    entities = [
        models.Offloading.base_date.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio,
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data
    ]

    stmt = select(*entities, *entities_groupby)

    # where

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading.base_date, start_date, end_date))

    txt_l = []
    ## code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Offloading.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Offloading.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.Offloading.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":  # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(models.Offloading.base_date.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_trend


# worst주요단말(데이터량기준) : 조 기준 X,
async def get_worst10_offloading_hndset_by_group_date(db: AsyncSession, code: str, group: str, start_date: str = None,
                                                       end_date: str = None,
                                                       limit: int = 10):
    sum_5g_data = func.sum(models.Offloading_Hndset.g5d_upld_data_qnt +
                           models.Offloading_Hndset.g5d_downl_data_qnt).label("sum_5g_data")
    sum_sru_data = func.sum(models.Offloading_Hndset.sru_usagecountdl +
                            models.Offloading_Hndset.sru_usagecountul).label("sum_sru_data")
    sum_3g_data = func.sum(models.Offloading_Hndset.g3d_upld_data_qnt +
                           models.Offloading_Hndset.g3d_downl_data_qnt).label("sum_3g_data")
    sum_lte_data = func.sum(models.Offloading_Hndset.ld_downl_data_qnt +
                            models.Offloading_Hndset.ld_upld_data_qnt).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading_Hndset.sido_nm + ' ', models.Offloading_Hndset.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading_Hndset.hndset_pet_nm,
    ]
    entities_groupby = [
        g5_off_ratio,
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading_Hndset.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Offloading_Hndset.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading_Hndset.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading_Hndset.new_center_nm.in_(txt_l))
    elif code == "팀별":
        # stmt = stmt.where(models.Offloading_Hndset.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":  # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 주요단말정렬기준 : 데이터량
    stmt = stmt.group_by(*entities)
    if limit <= 10:
        stmt = stmt.order_by(sum_total_data.desc()).limit(50)

    stmt_rk = select([
        # func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ]).order_by(stmt.c.g5_off_ratio.asc()).limit(limit)
    # print(stmt_rk.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_rk)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_offloading_bts = list(
        map(lambda x: schemas.OffloadingHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts


async def get_worst10_offloading_dong_by_group_date(db: AsyncSession, code: str, group: str, start_date: str = None,
                                                    end_date: str = None, limit: int = 10):
    sum_5g_data = func.sum(func.ifnull(models.Offloading_Bts.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading_Bts.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.Offloading_Bts.sru_usagecountdl, 0.0) +
                            func.ifnull(models.Offloading_Bts.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.Offloading_Bts.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading_Bts.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.Offloading_Bts.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.Offloading_Bts.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading_Bts.sido_nm + ' ', models.Offloading_Bts.gun_gu_nm + ' ' +
                       models.Offloading_Bts.eup_myun_dong_nm).label("juso")

    entities = [
        juso,
        # models.Offloading_Bts.biz_hq_nm.label("center"),
        # models.Offloading_Bts.oper_team_nm.label("team"),
        models.Offloading_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading_Bts.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Offloading_Bts.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading_Bts.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        stmt = stmt.where(models.Offloading_Bts.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Offloading_Bts.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":  # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.where(models.Offloading_Bts.area_jo_nm != "값없음")
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).limit(limit)

    stmt_rk = select([
        # func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ]).order_by(stmt.c.g5_off_ratio.asc()).limit(limit)
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_dong = list(
        map(lambda x: schemas.OffloadingDongOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_dong


async def get_offloading_trend_item_by_group_date(db: AsyncSession, code: str, group: str, start_date: str = None,
                                                  end_date: str = None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_5g_data = func.sum(func.ifnull(models.Offloading.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.Offloading.sru_usagecountdl, 0.0) +
                            func.ifnull(models.Offloading.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.Offloading.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.Offloading.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.Offloading.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4).label("value")

    entities = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio
    ]
    # where
    ## 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Offloading.base_date, start_date, end_date))

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.Offloading.mkng_cmpn_nm.in_(where_ins))
        code_column = models.Offloading.mkng_cmpn_nm

    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부", "") for txt in where_ins]
        stmt_where_and.append(models.Offloading.new_hq_nm.in_(where_ins))
        code_column = models.Offloading.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터", "") for txt in where_ins]
        stmt_where_and.append(models.Offloading.new_center_nm.in_(where_ins))
        code_column = models.Offloading.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(models.Offloading.oper_team_nm.in_(where_ins))
        code_column = models.Offloading.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(models.Offloading.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.Offloading.area_jo_nm.in_(where_ins))
        code_column = models.Offloading.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(models.Offloading.sido_nm.in_(where_ins))
        code_column = models.Offloading.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(models.Offloading.gun_gu_nm.in_(where_ins))
        code_column = models.Offloading.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(models.Offloading.eup_myun_dong_nm.in_(where_ins))
        code_column = models.Offloading.sido_nm

    elif code == "전국" or code == "전체" or code == "all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx

    # group by  : offloading은 상품선택이 없어 code로 고정
    by_column = code_column

    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.Offloading.base_date.label("date"),
        *entities,
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.Offloading.base_date,
               by_column)

    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.OffloadingTrendOutput(**r) for r in query_result if r[0] == code]
        list_items.append(schemas.OffloadingTrendItemOutput(title=code, data=t_l))
    return list_items


async def get_offloading_trend_by_group_month(db: AsyncSession, code: str, group: str, start_month: str = None,
                                              end_month: str = None):
    sum_5g_data = func.sum(func.ifnull(models.OffloadingMM.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.OffloadingMM.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.OffloadingMM.sru_usagecountdl, 0.0) +
                            func.ifnull(models.OffloadingMM.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.OffloadingMM.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.OffloadingMM.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.OffloadingMM.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.OffloadingMM.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")

    entities = [
        models.OffloadingMM.base_ym.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio,
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_month:
        end_month = start_month

    if start_month:
        # base_date list 생성
        stmt = stmt.where(between(models.OffloadingMM.base_ym, start_month, end_month))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.OffloadingMM.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.OffloadingMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        stmt = stmt.where(models.OffloadingMM.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.OffloadingMM.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.OffloadingMM.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.OffloadingMM.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt = stmt.where(models.OffloadingMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt = stmt.where(models.OffloadingMM.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt = stmt.where(models.OffloadingMM.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":  # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(models.OffloadingMM.base_ym.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))),
                                     query_result))
    return list_offloading_trend


async def get_offloading_trend_item_by_group_month(db: AsyncSession, code: str, group: str, start_month: str = None,
                                                   end_month: str = None):
    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_5g_data = func.sum(func.ifnull(models.OffloadingMM.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.OffloadingMM.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.OffloadingMM.sru_usagecountdl, 0.0) +
                            func.ifnull(models.OffloadingMM.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.OffloadingMM.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.OffloadingMM.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.OffloadingMM.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.OffloadingMM.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4).label("value")

    entities = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio
    ]

    # where
    ## 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    stmt_where_and.append(between(models.OffloadingMM.base_ym, start_month, end_month))

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.OffloadingMM.mkng_cmpn_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.mkng_cmpn_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.mkng_cmpn_nm)
    elif code == "본부별":
        code_tbl_nm = select(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm). \
            group_by(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).subquery()
        stmt_where_and.append(code_tbl_nm.c.bonbu_nm.in_(where_ins))
        stmt = select(
            func.replace(code_tbl_nm.c.bonbu_nm,"NW운용본부","").label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities
        ).outerjoin(
            code_tbl_nm,
            code_tbl_nm.c.biz_hq_nm == models.OffloadingMM.biz_hq_nm
        ).where(
            and_(*stmt_where_and)
        ).group_by(
            models.OffloadingMM.base_ym,
            code_tbl_nm.c.bonbu_nm
        )
        # 월Table에 new_hq_nm, new_center_nm 추가되면 변경
        # where_ins = [txt.replace("NW운용본부", "") for txt in where_ins]
        # stmt_where_and.append(models.OffloadingMM.new_hq_nm.in_(where_ins))
        # stmt = select(
        #     models.OffloadingMM.new_hq_nm.label("code"),
        #     models.OffloadingMM.base_ym.label("date"),
        #     *entities
        # ).where(
        #     and_(*stmt_where_and)
        # ).group_by(models.OffloadingMM.base_ym,
        #            models.OffloadingMM.new_hq_nm)
    elif code == "센터별":
        stmt_where_and.append(models.OffloadingMM.biz_hq_nm.in_(where_ins))
        stmt = select(
            func.replace(models.OffloadingMM.biz_hq_nm, "액세스운용센터","").label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.biz_hq_nm)

        # 월Table에 new_hq_nm, new_center_nm 추가되면 변경
        # where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        # stmt_where_and.append(models.OffloadingMM.new_center_nm.in_(where_ins))
        # stmt = select(
        #     models.OffloadingMM.new_center_nm.label("code"),
        #     models.OffloadingMM.base_ym.label("date"),
        #     *entities
        # ).where(
        #     and_(*stmt_where_and)
        # ).group_by(models.OffloadingMM.base_ym,
        #            models.OffloadingMM.new_center_nm)
    elif code == "팀별":
        stmt_where_and.append(models.OffloadingMM.oper_team_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.oper_team_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.oper_team_nm)
    elif code == "조별":
        stmt_where_and.append(models.OffloadingMM.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.OffloadingMM.area_jo_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.area_jo_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.area_jo_nm)
    elif code == "시도별":
        stmt_where_and.append(models.OffloadingMM.sido_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.sido_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.sido_nm)
    elif code == "시군구별":
        stmt_where_and.append(models.OffloadingMM.gun_gu_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.gun_gu_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.gun_gu_nm)
    elif code == "읍면동별":
        stmt_where_and.append(models.OffloadingMM.eup_myun_dong_nm.in_(where_ins))
        stmt = select(
            models.OffloadingMM.eup_myun_dong_nm.label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   models.OffloadingMM.eup_myun_dong_nm)
    elif code == "전국" or code =="전체" or code == "all":
        stmt = select(
            literal("all").label("code"),
            models.OffloadingMM.base_ym.label("date"),
            *entities,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.OffloadingMM.base_ym,
                   literal("all"))

    else:
        raise ex.NotFoundAccessKeyEx

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.OffloadingTrendOutput(**r) for r in query_result if r[0] == code]
        list_items.append(schemas.OffloadingTrendItemOutput(title=code, data=t_l))
    return list_items