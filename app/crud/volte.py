from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_
from datetime import datetime, timedelta


async def get_worst10_volte_bts_by_group_date2(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                        start_date: str=None, end_date: str=None, limit: int=10):
    # 5G VOLTE 절단호 worst 10 기지국
    sum_try = func.sum(func.ifnull(models.VolteFailBts.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.ifnull(models.VolteFailBts.comp_cacnt, 0.0)).label("sum_suc")
    # sum_fail = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_fail")
    sum_cut = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.VolteFailBts.sido_nm+' ', models.VolteFailBts.eup_myun_dong_nm).label("juso")

    entities = [
        models.VolteFailBts.equip_nm,
        models.VolteFailBts.equip_cd,
        # juso,
        models.VolteFailBts.biz_hq_nm.label("center"),
        models.VolteFailBts.oper_team_nm.label("team"),
        models.VolteFailBts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        # sum_fail,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby)

    #기간
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VolteFailBts.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VolteFailBts.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(stmt_where))
    elif code == "팀별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(stmt_where))
    elif code == "조별":
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VolteFailBts.anals_3_prod_level_nm == prod)

    # stmt = stmt.group_by(*entities).having(sum_try>100).order_by(sum_cut.desc()).subquery()
    stmt = stmt.group_by(*entities).having(sum_try>100).order_by(sum_cut.desc()).limit(limit)
    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_bts


async def get_worst10_volte_hndset_by_group_date2(db: AsyncSession, prod:str=None, code:str=None, group: str=None,
                                           start_date: str = None, end_date: str=None, limit: int = 10):
    # VOLTE 절단율 worst 10 단말기
    sum_try = func.sum(func.ifnull(models.VolteFailHndset.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.ifnull(models.VolteFailHndset.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailHndset.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.VolteFailHndset.hndset_pet_nm,
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.VolteFailHndset.base_date, start_date, end_date))

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VolteFailHndset.anals_3_prod_level_nm == prod)

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VolteFailHndset.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.oper_team_nm.in_(stmt_where))
    elif code == "팀별":
        stmt = stmt.where(models.VolteFailHndset.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    # stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(sum_cut.desc()).subquery()
    stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(sum_cut.desc()).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    print(stmt_rk)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_volte_hndset = list(map(lambda x: schemas.VolteHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_hndset


async def get_volte_trend_by_group_date2(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_date: str=None, end_date: str=None):
    sum_suc = func.sum(func.ifnull(models.VolteFailOrg.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailOrg.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    fc_373_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc9563_cnt, 0.0)).label("fc_9563")

    entities_cut = [
        models.VolteFailOrg.base_date.label("date"),
    ]
    entities_groupby_cut = [
        cut_ratio,
        fc_373_cnt,
        fc_9563_cnt
    ]

    stmt_cut = select(*entities_cut, *entities_groupby_cut)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt_cut = stmt_cut.where(between(models.VolteFailOrg.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")


    # 선택 조건
    if code == "제조사별":
        stmt_cut = stmt_cut.where(models.VolteFailOrg.mkng_cmpn_nm.in_(txt_l))
    elif code == "센터별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(stmt_where))
    elif code == "팀별":
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(stmt_where))
    elif code == "조별":
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt_cut = stmt_cut.where(models.VolteFailOrg.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    # 상품 조건
    if prod and prod != "전체":
        stmt_cut = stmt_cut.where(models.VolteFailOrg.anals_3_prod_level_nm == prod)

    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.VolteFailOrg.base_date.asc())

    print(stmt_cut.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys_cut, x))), query_result_cut))
    return list_volte_trend


async def get_volte_trend_item_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_date: str=None, end_date: str=None):
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    sum_suc = func.sum(func.ifnull(models.VolteFailOrg.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailOrg.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = func.round(sum_cut / (sum_suc + 1e-6) * 100, 4).label("cut_rate")

    fc_373_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc9563_cnt, 0.0)).label("fc_9563")

    # 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.VolteFailOrg.base_date, start_date, end_date))

    # 상품 조건
    if prod and prod != "전체":
        stmt_where_and.append(models.VolteFailOrg.anals_3_prod_level_nm == prod)

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_sel_nm = models.VolteFailOrg.mkng_cmpn_nm

    elif code == "센터별":
        code_tbl_nm = models.OrgCode
        code_sel_nm = models.OrgCode.area_jo_nm
        code_where_nm = models.OrgCode.biz_hq_nm

        stmt_sel_nm = models.VolteFailOrg.area_jo_nm
    elif code == "팀별":
        code_tbl_nm = models.OrgCode
        code_sel_nm = models.OrgCode.area_jo_nm
        code_where_nm = models.OrgCode.oper_team_nm

        stmt_sel_nm = models.VolteFailOrg.area_jo_nm
    elif code == "조별":
        stmt_sel_nm = models.VolteFailOrg.area_jo_nm
    elif code == "시도별":
        code_tbl_nm = models.AddrCode
        code_sel_nm = models.AddrCode.eup_myun_dong_nm
        code_where_nm = models.AddrCode.sido_nm

        stmt_sel_nm = models.VolteFailOrg.eup_myun_dong_nm
    elif code == "시군구별":
        code_tbl_nm = models.AddrCode
        code_sel_nm = models.AddrCode.eup_myun_dong_nm
        code_where_nm = models.AddrCode.gun_gu_nm

        stmt_sel_nm = models.VolteFailOrg.eup_myun_dong_nm
    elif code == "읍면동별":
        stmt_sel_nm = models.VolteFailOrg.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if not code_tbl_nm:  # code table 미사용시
        stmt_where_and.append(stmt_sel_nm.in_(where_ins))

        stmt = select(
            stmt_sel_nm.label("code"),
            models.VolteFailOrg.base_date.label("date"),
            cut_ratio,
            fc_373_cnt,
            fc_9563_cnt,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.VolteFailOrg.base_date, stmt_sel_nm)
    else:  # code table 사용시
        stmt_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        stmt_where_and.append(stmt_sel_nm.in_(stmt_wh))

        st_in = select(
            models.VolteFailOrg.base_date,
            stmt_sel_nm.label("code"),
            sum_cut,
            sum_suc,
            fc_373_cnt,
            fc_9563_cnt,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.VolteFailOrg.base_date, stmt_sel_nm)

        stmt = select(
            code_where_nm.label("code"),
            st_in.c.base_date.label("date"),
            func.round(func.sum(st_in.c.sum_cut) / (func.sum(st_in.c.sum_suc) + 1e-6) * 100, 4).label("cut_rate"),
            func.sum(st_in.c.fc_373).label("fc_373"),
            func.sum(st_in.c.fc_9563).label("fc_9563"),
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in.c.code
        ).group_by(
            st_in.c.base_date,
            code_where_nm
        )

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.VolteTrendOutput(date=r[1], cut_rate=r[2], fc_373=r[3], fc_9563=r[4]) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.VolteTrendItemOutput(title=code, data=t_l))
    return list_items

############################
async def get_worst10_volte_bts_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                                        limit: int = 10):
    # 5G VOLTE 절단호기준 worst 10 기지국 :
    # get_worst10_volte_bts_by_group_date(db: Session, group: str = None, start_date: str=None, end_date: str=None, limit: int=10):
    sum_try = func.sum(func.ifnull(models.VolteFailBts.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.ifnull(models.VolteFailBts.comp_cacnt, 0.0)).label("sum_suc")
    # sum_fail = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_fail")
    sum_cut = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.VolteFailBts.sido_nm + ' ', models.VolteFailBts.eup_myun_dong_nm).label("juso")

    entities = [
        models.VolteFailBts.equip_nm,
        models.VolteFailBts.equip_cd,
        # juso,
        models.VolteFailBts.biz_hq_nm.label("center"),
        models.VolteFailBts.oper_team_nm.label("team"),
        models.VolteFailBts.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        # sum_fail,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby).where(models.VolteFailBts.anals_3_prod_level_nm == '5G')

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.VolteFailBts.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    if group.endswith("센터"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(stmt_where))
    elif group.endswith("팀") or group.endswith("부"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(stmt_where))
    elif group.endswith("조"):
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(txt_l))
    else:
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(txt_l))

    # stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(cut_ratio.desc()).subquery()
    stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(cut_ratio.desc())
    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])
    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_bts


async def get_worst10_volte_hndset_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                                           limit: int = 10):
    # 5G VOLTE 절단율 worst 10 단말기
    sum_try = func.sum(func.ifnull(models.VolteFailHndset.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.ifnull(models.VolteFailHndset.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailHndset.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.VolteFailHndset.hndset_pet_nm,
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby).where(models.VolteFailHndset.anals_3_prod_level_nm == '5G')

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.VolteFailHndset.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    if group.endswith("센터"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.area_jo_nm.in_(stmt_where))
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VolteFailHndset.oper_team_nm.in_(txt_l))
    else:
        stmt = stmt.where(models.VolteFailHndset.oper_team_nm.in_(txt_l))

    # stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(cut_ratio.desc()).subquery()
    stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(cut_ratio.desc())

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    print(stmt_rk)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_volte_hndset = list(map(lambda x: schemas.VolteHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_hndset


async def get_volte_trend_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None):
    sum_suc = func.sum(func.ifnull(models.VolteFailOrg.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailOrg.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    fc_373_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.ifnull(models.VolteFailOrg.fc9563_cnt, 0.0)).label("fc_9563")

    entities_cut = [
        models.VolteFailOrg.base_date.label("date"),
    ]
    entities_groupby_cut = [
        cut_ratio,
        fc_373_cnt,
        fc_9563_cnt
    ]

    stmt_cut = select(*entities_cut, *entities_groupby_cut).where(models.VolteFailOrg.anals_3_prod_level_nm == '5G')

    if not end_date:
        end_date = start_date

    if start_date:
        stmt_cut = stmt_cut.where(between(models.VolteFailOrg.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")


    if group.endswith("센터"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(stmt_where))
    elif group.endswith("팀") or group.endswith("부"):
        stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(stmt_where))
    elif group.endswith("조"):
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(txt_l))
    else:
        stmt_cut = stmt_cut.where(models.VolteFailOrg.area_jo_nm.in_(txt_l))

    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.VolteFailOrg.base_date.asc())

    query_cut = await db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys_cut, x))), query_result_cut))
    return list_volte_trend

async def get_volte_event_by_group_date(db: AsyncSession, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    ref_day = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    in_cond = [ref_day, today]

    sum_suc = func.sum(func.ifnull(models.VolteFailBts.comp_cacnt, 0.0))
    sum_cut = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.VolteFailBts.base_date,
        # models.VolteFailBts.area_jo_nm
    ]
    entities_groupby = [
        cut_ratio
    ]

    if group.endswith("센터"):
        select_group = models.VolteFailBts.biz_hq_nm
    elif group.endswith("팀") or group.endswith("부"):
        select_group = models.VolteFailBts.oper_team_nm
    elif group.endswith("조"):
        select_group = models.VolteFailBts.area_jo_nm
    else:
        select_group = None

    if select_group:
        entities.append(select_group)
        stmt = select([*entities, *entities_groupby], models.VolteFailBts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.VolteFailBts.base_date.asc())
        stmt = stmt.where(select_group == group)
    else:
        stmt = select([*entities, *entities_groupby], models.VolteFailBts.base_date.in_(in_cond)). \
            group_by(*entities).order_by(models.VolteFailBts.base_date.asc())
    try:
        query = await db.execute(stmt)
        query_result = query.all()
        query_keys = query.keys()
        result = list(zip(*query_result))
        values = result[-1]
        dates = result[0]
    except:
        return None
    # print("date: ", in_cond)
    # print("resut: ", result)
    # print("keys: ", query_keys)
    # print(dict(zip(query_keys, result)))

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

    volte_event = schemas.VolteEventOutput(
        title = "VoLTE 절단율(전일대비)",
        score = score,
        score_ref = score_ref,
    )
    return volte_event