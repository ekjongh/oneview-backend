from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_
from datetime import datetime, timedelta


async def get_offloading_trend_by_group_date2(db: AsyncSession, code:str, group: str, start_date: str=None, end_date: str=None):
    sum_5g_data = func.sum(func.ifnull(models.Offloading_Bts.g5d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading_Bts.g5d_downl_data_qnt,0.0)).label("sum_5g_data")
    sum_sru_data = func.sum(func.ifnull(models.Offloading_Bts.sru_usagecountdl, 0.0) +
                            func.ifnull(models.Offloading_Bts.sru_usagecountul, 0.0)).label("sum_sru_data")
    sum_3g_data = func.sum(func.ifnull(models.Offloading_Bts.g3d_upld_data_qnt, 0.0) +
                           func.ifnull(models.Offloading_Bts.g3d_downl_data_qnt, 0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.Offloading_Bts.ld_downl_data_qnt, 0.0) +
                            func.ifnull(models.Offloading_Bts.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")
    
    entities = [
        models.Offloading_Bts.base_date.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio
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
    elif code == "센터별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "팀별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "조별":
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_trend

# 주요단말(데이터량기준)
async def get_worst10_offloading_hndset_by_group_date2(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None,
                                            limit: int = 10):
    sum_5g_data = func.sum(models.Offloading_Hndset.g5d_upld_data_qnt +
                models.Offloading_Hndset.g5d_downl_data_qnt).label("sum_5g_data")
    sum_sru_data = func.sum( models.Offloading_Hndset.sru_usagecountdl +
                 models.Offloading_Hndset.sru_usagecountul).label("sum_sru_data")
    sum_3g_data = func.sum( models.Offloading_Hndset.g3d_upld_data_qnt +
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
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
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
    elif code == "센터별":
        stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm.in_(stmt_where))
    elif code == "팀별":
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Hndset.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    #주요단말정렬기준 : 데이터량
    # stmt = stmt.group_by(*entities).order_by(sum_total_data.asc()).subquery()
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
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
        # models.Offloading_Bts.equip_nm,
        # models.Offloading_Bts.equip_cd,
        juso,
        models.Offloading_Bts.biz_hq_nm.label("center"),
        models.Offloading_Bts.oper_team_nm.label("team"),
        models.Offloading_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
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
        stmt_cut = stmt.where(models.Offloading_Bts.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "팀별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "조별":
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    # stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.group_by(*entities).having(sum_total_data > 0).order_by(g5_off_ratio.asc()).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_dong = list(
        map(lambda x: schemas.OffloadingDongOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_dong


async def get_offloading_trend_item_by_group_date(db: AsyncSession, code: str, group: str, start_date: str = None,
                                        end_date: str = None):
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

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
    g5_off_ratio = func.round(g5_off_ratio, 4).label("value")

    # 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Offloading_Bts.base_date, start_date, end_date))

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_sel_nm = models.Offloading_Bts.mkng_cmpn_nm

    elif code == "센터별":
        code_tbl_nm = models.OrgCode
        code_sel_nm = models.OrgCode.area_jo_nm
        code_where_nm = models.OrgCode.biz_hq_nm

        stmt_sel_nm = models.Offloading_Bts.area_jo_nm
    elif code == "팀별":
        code_tbl_nm = models.OrgCode
        code_sel_nm = models.OrgCode.area_jo_nm
        code_where_nm = models.OrgCode.oper_team_nm

        stmt_sel_nm = models.Offloading_Bts.area_jo_nm
    elif code == "조별":
        stmt_sel_nm = models.Offloading_Bts.area_jo_nm
    elif code == "시도별":
        code_tbl_nm = models.AddrCode
        code_sel_nm = models.AddrCode.eup_myun_dong_nm
        code_where_nm = models.AddrCode.sido_nm

        stmt_sel_nm = models.Offloading_Bts.eup_myun_dong_nm
    elif code == "시군구별":
        code_tbl_nm = models.AddrCode
        code_sel_nm = models.AddrCode.eup_myun_dong_nm
        code_where_nm = models.AddrCode.gun_gu_nm

        stmt_sel_nm = models.Offloading_Bts.eup_myun_dong_nm
    elif code == "읍면동별":
        stmt_sel_nm = models.Offloading_Bts.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if not code_tbl_nm:  # code table 미사용시
        stmt_where_and.append(stmt_sel_nm.in_(where_ins))

        stmt = select(
            stmt_sel_nm.label("code"),
            models.Offloading_Bts.base_date.label("date"),
            g5_off_ratio,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Offloading_Bts.base_date, stmt_sel_nm)

    else:  # code table 사용시
        stmt_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        stmt_where_and.append(stmt_sel_nm.in_(stmt_wh))

        st_in = select(
            stmt_sel_nm.label("code"),
            models.Offloading_Bts.base_date,
            sum_5g_data,
            sum_sru_data,
            sum_total_data,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Offloading_Bts.base_date, stmt_sel_nm)

        stmt = select(
            code_where_nm.label("code"),
            st_in.c.base_date.label("date"),
            func.round((func.sum(st_in.c.sum_5g_data)+func.sum(st_in.c.sum_sru_data))/
                        (func.sum(st_in.c.sum_total_data) + 1e-6) * 100, 4).label("value"),
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in.c.code
        ).group_by(
            st_in.c.base_date,
            code_where_nm
        )


    query = await db.execute(stmt)
    query_result = query.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.OffloadingTrendOutput(date=r[1], value=r[2]) for r in query_result if r[0] == code]
        list_items.append(schemas.OffloadingTrendItemOutput(title=code, data=t_l))
    return list_items


#############################################
async def get_worst10_offloading_jo_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                                            limit: int = 10):
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
    # juso = func.concat(models.Offloading_Bts.sido_nm+' ', models.Offloading_Bts.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading_Bts.equip_nm,
        models.Offloading_Bts.equip_cd,
        # juso,
        models.Offloading_Bts.biz_hq_nm.label("center"),
        models.Offloading_Bts.oper_team_nm.label("team"),
        models.Offloading_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
        g5_off_ratio,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading_Bts.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading_Bts.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)
    else:
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm == group)

    # stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc())

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(
        map(lambda x: schemas.OffloadingBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts


async def get_offloading_trend_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None):
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
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("value")

    entities = [
        models.Offloading_Bts.base_date.label("date"),
    ]
    entities_groupby = [
        g5_off_ratio
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

    if group.endswith("센터"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif group.endswith("팀") or group.endswith("부"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif group.endswith("조"):
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))
    else:
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))

    stmt = stmt.group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_trend

async def get_worst10_offloading_hndset_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                                            limit: int = 10):
    sum_5g_data = func.sum(func.ifnull(models.Offloading_Hndset.g5d_upld_data_qnt, 0.0) +
                func.ifnull(models.Offloading_Hndset.g5d_downl_data_qnt, 0.0)).label("sum_5g_data")
    sum_sru_data = func.sum( func.ifnull(models.Offloading_Hndset.sru_usagecountdl, 0.0) +
                 func.ifnull(models.Offloading_Hndset.sru_usagecountul,0.0)).label("sum_sru_data")
    sum_3g_data = func.sum( func.ifnull(models.Offloading_Hndset.g3d_upld_data_qnt, 0.0) +
                 func.ifnull(models.Offloading_Hndset.g3d_downl_data_qnt,0.0)).label("sum_3g_data")
    sum_lte_data = func.sum(func.ifnull(models.Offloading_Hndset.ld_downl_data_qnt, 0.0) +
                 func.ifnull(models.Offloading_Hndset.ld_upld_data_qnt, 0.0)).label("sum_lte_data")
    sum_total_data = (sum_3g_data + sum_lte_data + sum_5g_data).label("sum_total_data")
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading_Hndset.sido_nm + ' ', models.Offloading_Hndset.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading_Hndset.hndset_pet_nm,
    ]
    entities_groupby = [
        g5_off_ratio
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Offloading_Hndset.base_date, start_date, end_date))

    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading_Hndset.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm == group)
    else:
        stmt = stmt.where(models.Offloading_Hndset.oper_team_nm == group)

    # stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc())

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(
        map(lambda x: schemas.OffloadingHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts


# 미사용
async def get_worst10_offloading_jo_by_group_date2(db: AsyncSession, code: str, group: str, start_date: str = None,
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
        models.Offloading_Bts.equip_nm,
        models.Offloading_Bts.equip_cd,
        # juso,
        models.Offloading_Bts.biz_hq_nm.label("center"),
        models.Offloading_Bts.oper_team_nm.label("team"),
        models.Offloading_Bts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        # sum_3g_data,
        # sum_lte_data,
        # sum_5g_data,
        # sum_sru_data,
        # sum_total_data,
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
        stmt_cut = stmt.where(models.Offloading_Bts.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "팀별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
    elif code == "조별":
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Offloading_Bts.eup_myun_dong_nm.in_(txt_l))
    else:
        stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(txt_l))

    # stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_offloading_offloading_bts = list(
        map(lambda x: schemas.OffloadingBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_offloading_bts

#미사용
async def get_offloading_event_by_group_date(db: AsyncSession, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

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

    entities = [
        models.Offloading_Bts.base_date,
        # models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        g5_off_ratio
    ]

    if group.endswith("센터"):
        select_group = models.Offloading_Bts.biz_hq_nm
    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.Offloading_Bts.oper_team_nm
    elif group.endswith("조"):
        select_group = models.Offloading_Bts.area_jo_nm
    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.Offloading_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.Offloading_Bts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())
    try:
        query = await db.execute(stmt)
        query_result = query.all()
        query_keys = query.keys()
        result = list(zip(*query_result))
        values = result[-1]
        dates = result[0]
    except:
        return None

    if len(values) == 1:
        if today in dates:
            score = values[0]
            score_ref = 0
        else:
            score = 0
            score_ref = values[0]
    else:
        score = values[1]
        score_ref = values[0]

    offloading_event = schemas.OffloadingEventOutput(
        title = "5G 오프로딩 (전일대비)",
        score = score,
        score_ref = score_ref,
    )
    return offloading_event
