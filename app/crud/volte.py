from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_, or_, literal
from datetime import datetime, timedelta
from app.utils.query_utils import band_to_equipcd2

async def get_worst10_volte_bts_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                        band:str=None,start_date: str=None, end_date: str=None, limit: int=10):
    # 5G VOLTE 절단호 worst 10 기지국
    sum_try = func.sum(func.ifnull(models.VolteFailBts.try_cacnt, 0.0)).label("sum_try")
    sum_suc = func.sum(func.ifnull(models.VolteFailBts.comp_cacnt, 0.0)).label("sum_suc")
    # sum_fail = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_fail")
    sum_cut = func.sum(func.ifnull(models.VolteFailBts.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.VolteFailBts.gun_gu_nm+' ', models.VolteFailBts.eup_myun_dong_nm).label("juso")

    entities = [
        models.VolteFailBts.equip_nm,
        models.VolteFailBts.equip_cd,
        # juso,
        # models.VolteFailBts.biz_hq_nm.label("center"),
        # models.VolteFailBts.oper_team_nm.label("team"),
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
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt = stmt.where(models.VolteFailBts.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.VolteFailBts.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.VolteFailBts.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.VolteFailBts.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VolteFailBts.eup_myun_dong_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건 (5g, lte  : DB에도 2개만 존재)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt = stmt.where(models.VolteFailBts.anals_3_prod_level_nm.in_(prod_l))

    # 주파수대역 조건
    if band :
        equipcd2 = band_to_equipcd2(band)
        stmt = stmt.where(func.substring(models.VolteFailBts.equip_cd,1,2).in_(equipcd2))


    # stmt = stmt.group_by(*entities).having(sum_try>100).order_by(sum_cut.desc()).subquery()
    stmt = stmt.where(models.VolteFailBts.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).having(sum_try>100).order_by(cut_ratio.desc()).limit(limit)
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


# 조기준X
async def get_worst10_volte_hndset_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group: str=None,
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

    # 상품 조건 (5g_sa, 5g)
    if prod == "5G-SA":
        stmt = stmt.where(models.VolteFailHndset.anals_3_prod_level_nm == '5G')
        stmt = stmt.where(models.VolteFailHndset.sa_5g_suprt_div_nm == '5G_SA지원')
    elif prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt = stmt.where(models.VolteFailHndset.anals_3_prod_level_nm.in_(prod_l))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VolteFailHndset.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt = stmt.where(models.VolteFailHndset.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.VolteFailHndset.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.VolteFailHndset.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VolteFailHndset.eup_myun_dong_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # stmt = stmt.group_by(*entities).having(sum_try > 100).order_by(sum_cut.desc()).subquery()
    stmt = stmt.group_by(*entities)
    if limit <= 10 :
        stmt = stmt.order_by(sum_cut.desc()).limit(50)

    stmt_rk = select([
        # func.rank().over(order_by=stmt.c.cut_ratio.desc()).label("RANK"),
        *stmt.c
    ]).order_by(stmt.c.cut_ratio.desc()).limit(limit)

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt_rk)
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_volte_hndset = list(map(lambda x: schemas.VolteHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_volte_hndset


async def get_volte_trend_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_date: str=None, end_date: str=None):
    sum_suc = func.sum(func.ifnull(models.VolteFail.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFail.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    fc_373_cnt = func.sum(func.ifnull(models.VolteFail.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.ifnull(models.VolteFail.fc9563_cnt, 0.0)).label("fc_9563")

    entities_cut = [
        models.VolteFail.base_date.label("date"),
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
        stmt_cut = stmt_cut.where(between(models.VolteFail.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_cut = stmt_cut.where(models.VolteFail.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_cut = stmt_cut.where(models.VolteFail.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_cut = stmt_cut.where(models.VolteFail.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_cut = stmt_cut.where(models.VolteFail.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt_cut = stmt_cut.where(models.VolteFail.area_jo_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFail.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFail.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFail.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt_cut = stmt_cut.where(models.VolteFail.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건(5g, lte)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_cut = stmt_cut.where(models.VolteFail.anals_3_prod_level_nm.in_(prod_l))

    stmt_cut = stmt_cut.where(models.VolteFail.area_jo_nm!="값없음")
    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.VolteFail.base_date.asc())
    # print(stmt_cut.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys_cut, x))), query_result_cut))
    return list_volte_trend


async def get_volte_trend_item_by_group_date(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  by:str="code", start_date: str=None, end_date: str=None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_suc = func.sum(func.ifnull(models.VolteFail.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFail.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = func.round(sum_cut / (sum_suc + 1e-6) * 100, 4).label("cut_rate")
    fc_373_cnt = func.sum(func.ifnull(models.VolteFail.fc373_cnt, 0.0)).label("fc_373")
    fc_9563_cnt = func.sum(func.ifnull(models.VolteFail.fc9563_cnt, 0.0)).label("fc_9563")

    # where
    ## 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.VolteFail.base_date, start_date, end_date))

    ## 상품 조건(5g, lte)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.VolteFail.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.VolteFail.anals_3_prod_level_nm
    else:
        prod_column = models.VolteFail.anals_3_prod_level_nm

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.VolteFail.mkng_cmpn_nm.in_(where_ins))
        code_column = models.VolteFail.mkng_cmpn_nm

    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.VolteFail.new_hq_nm.in_(where_ins))
        code_column = models.VolteFail.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        stmt_where_and.append(models.VolteFail.new_center_nm.in_(where_ins))
        code_column = models.VolteFail.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(models.VolteFail.oper_team_nm.in_(where_ins))
        code_column = models.VolteFail.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(models.VolteFail.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.VolteFail.area_jo_nm.in_(where_ins))
        code_column = models.VolteFail.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(models.VolteFail.sido_nm.in_(where_ins))
        code_column = models.VolteFail.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(models.VolteFail.gun_gu_nm.in_(where_ins))
        code_column = models.VolteFail.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(models.VolteFail.eup_myun_dong_nm.in_(where_ins))
        code_column = models.VolteFail.eup_myun_dong_nm

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
        by_column = literal("all")
    else:
        by_column = code_column

    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.VolteFail.base_date.label("date"),
        cut_ratio,
        fc_373_cnt,
        fc_9563_cnt,
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.VolteFail.base_date,
               by_column)

    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.VolteTrendOutput(**r) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.VolteTrendItemOutput(title=code, data=t_l))
    return list_items



async def get_volte_trend_by_group_month(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  start_month: str=None, end_month: str=None):
    sum_suc = func.sum(func.ifnull(models.VolteFailMM.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailMM.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_rate")

    entities_cut = [
        models.VolteFailMM.base_ym.label("date"),
    ]
    entities_groupby_cut = [
        cut_ratio,
        sum_suc,
        sum_cut
    ]

    stmt_cut = select(*entities_cut, *entities_groupby_cut)

    if not end_month:
        end_month = start_month

    if start_month:
        stmt_cut = stmt_cut.where(between(models.VolteFailMM.base_ym, start_month, end_month))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_cut = stmt_cut.where(models.VolteFailMM.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_cut = stmt_cut.where(models.VolteFailMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_cut = stmt_cut.where(models.VolteFailMM.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_cut = stmt_cut.where(models.VolteFailMM.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt_cut = stmt_cut.where(models.VolteFailMM.area_jo_nm.in_(txt_l))
        stmt_cut = stmt_cut.where(models.VolteFailMM.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        # stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.sido_nm.in_(txt_l))
        # stmt_cut = stmt_cut.where(models.VolteFailMM.eup_myun_dong_nm.in_(stmt_where))
        stmt_cut = stmt_cut.where(models.VolteFailMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        # stmt_where = select(models.AddrCode.eup_myun_dong_nm).distinct().where(models.AddrCode.gun_gu_nm.in_(txt_l))
        # stmt_cut = stmt_cut.where(models.VolteFailMM.eup_myun_dong_nm.in_(stmt_where))
        stmt_cut = stmt_cut.where(models.VolteFailMM.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_cut = stmt_cut.where(models.VolteFailMM.eup_myun_dong_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건(5g, lte)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_cut = stmt_cut.where(models.VolteFailMM.anals_3_prod_level_nm.in_(prod_l))

    stmt_cut = stmt_cut.where(models.VolteFailMM.area_jo_nm!="값없음")
    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.VolteFailMM.base_ym.asc())
    # print(stmt_cut.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt_cut)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(**dict(zip(query_keys_cut, x))), query_result_cut))
    return list_volte_trend


async def get_volte_trend_item_by_group_month(db: AsyncSession, prod:str=None, code:str=None, group:str=None,
                                  by:str="code", start_month: str=None, end_month: str=None):

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_suc = func.sum(func.ifnull(models.VolteFailMM.comp_cacnt, 0.0)).label("sum_suc")
    sum_cut = func.sum(func.ifnull(models.VolteFailMM.fail_cacnt, 0.0)).label("sum_cut")
    cut_ratio = func.round(sum_cut / (sum_suc + 1e-6) * 100, 4).label("cut_rate")
    # fc_373_cnt = func.sum(func.ifnull(models.VolteFailMM.fc373_cnt, 0.0)).label("fc_373")
    # fc_9563_cnt = func.sum(func.ifnull(models.VolteFailMM.fc9563_cnt, 0.0)).label("fc_9563")

    # where
    ## 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    stmt_where_and.append(between(models.VolteFailMM.base_ym, start_month, end_month))

    ## 상품 조건(5g, lte)
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.VolteFailMM.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.VolteFailMM.anals_3_prod_level_nm
    else:
        prod_column = models.VolteFailMM.anals_3_prod_level_nm

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")
    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.VolteFailMM.mkng_cmpn_nm.in_(where_ins))
        code_column = models.VolteFailMM.mkng_cmpn_nm

    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.VolteFailMM.new_hq_nm.in_(where_ins))
        code_column = models.VolteFailMM.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        stmt_where_and.append(models.VolteFailMM.new_center_nm.in_(where_ins))
        code_column = models.VolteFailMM.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(models.VolteFailMM.oper_team_nm.in_(where_ins))
        code_column = models.VolteFailMM.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(models.VolteFailMM.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.VolteFailMM.area_jo_nm.in_(where_ins))
        code_column = models.VolteFailMM.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(models.VolteFailMM.sido_nm.in_(where_ins))
        code_column = models.VolteFailMM.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(models.VolteFailMM.gun_gu_nm.in_(where_ins))
        code_column = models.VolteFailMM.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(models.VolteFailMM.eup_myun_dong_nm.in_(where_ins))
        code_column = models.VolteFailMM.eup_myun_dong_nm

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
        by_column = literal("all")
    else:
        by_column = code_column


    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.VolteFailMM.base_ym.label("date"),
        cut_ratio,
        sum_suc,
        sum_cut,
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.VolteFailMM.base_ym,
                by_column)
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result_cut = query_cut.all()
    query_keys_cut = query_cut.keys()

    code_set = set([r[0] for r in query_result_cut])
    list_items = []
    for code in code_set:
        t_l = [schemas.VolteTrendOutput(**r) for r in query_result_cut if r[0] == code]
        list_items.append(schemas.VolteTrendItemOutput(title=code, data=t_l))
    return list_items