from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_, or_, literal
from datetime import datetime, timedelta

from app.utils.query_utils import band_to_equipcd2


async def get_rrc_trend_by_group_date(db: AsyncSession, code:str, group:str, start_date:str = None, end_date: str = None):
    # model_tbl = models.RrcTrend
    model_tbl = models.Rrc

    sum_rrc_try = func.sum(func.ifnull(model_tbl.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(model_tbl.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    # sum_prb_avg = func.sum(func.ifnull(model_tbl.sum_prb_avg, 0.0))
    # cnt_prb_avg = func.sum(func.ifnull(model_tbl.cnt_prb_avg, 0.0))
    # prbusage_mean = func.round((sum_prb_avg/cnt_prb_avg+ 1e-6) * 100, 4).label("prbusage_mean")
    prbusage_mean = func.round(func.avg(model_tbl.prb_avg) * 100, 4).label("prbusage_mean")

    entities = [
        model_tbl.base_date.label("date"),
    ]
    entities_groupby = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(model_tbl.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(model_tbl.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(model_tbl.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(model_tbl.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(model_tbl.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(model_tbl.area_jo_nm.in_(txt_l))
        stmt = stmt.where(model_tbl.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(model_tbl.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(model_tbl.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(model_tbl.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(model_tbl.base_date.asc())
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_rrc_trend = list(map(lambda x: schemas.RrcTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_rrc_trend


async def get_worst10_rrc_bts_by_group_date(db: AsyncSession, prod:str, code:str, group: str,band:str,
                                             start_date: str = None, end_date: str = None, limit: int = 10):
    sum_rrc_try = func.sum(func.ifnull(models.Rrc.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.Rrc.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prb_avg) * 100, 4).label("prbusage_mean")
    juso = func.concat(models.Rrc.sido_nm + ' ', models.Rrc.eup_myun_dong_nm).label("juso")

    entities = [
        models.Rrc.equip_cd.label("equip_cd"),
        models.Rrc.equip_nm.label("equip_nm"),
        # juso,
        # models.Rrc.area_center_nm.label("center"),
        # models.Rrc.oper_team_nm.label("team"),
        models.Rrc.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Rrc.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Rrc.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.Rrc.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.Rrc.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.Rrc.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.Rrc.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.Rrc.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Rrc.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Rrc.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Rrc.eup_myun_dong_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 주파수대역 조건
    if band :
        equipcd2 = band_to_equipcd2(band)
        stmt = stmt.where(func.substring(models.Rrc.equip_cd,1,2).in_(equipcd2))

    #worst 기준(RRC성공률, 트래픽, PRB부하율)
    if prod == "RRC성공률":
        order_col = rrc_rate.asc()
    elif prod == "트래픽":
        order_col = sum_rrc_try.desc()
    elif prod == "PRB사용율":
        order_col = prbusage_mean.desc()
    else:
        order_col = rrc_rate.asc()

    # stmt = stmt.group_by(*entities).having(sum_rrc_try>0).order_by(rrc_rate.desc()).subquery()
    stmt = stmt.where(models.Rrc.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).having(sum_rrc_try>0).order_by(order_col).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.rrc_rate.asc()).label("RANK"),
        *stmt.c
    ])
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_rrc_bts = list(map(lambda x: schemas.RrcBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_rrc_bts


async def get_rrc_trend_item_by_group_date(db: AsyncSession, code:str, group:str, start_date:str = None, end_date: str = None):
    # model_tbl = models.RrcTrend
    model_tbl = models.Rrc
    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_rrc_try = func.sum(func.ifnull(model_tbl.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(model_tbl.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(model_tbl.prb_avg) * 100, 4).label("prbusage_mean")
    # sum_prb_avg = func.sum(func.ifnull(model_tbl.sum_prb_avg, 0.0)).label("sum_prb_avg")
    # cnt_prb_avg = func.sum(func.ifnull(model_tbl.cnt_prb_avg, 0.0)).label("cnt_prb_avg")
    # prbusage_mean = func.round((sum_prb_avg / cnt_prb_avg + 1e-6) * 100, 4).label("prbusage_mean")

    entities = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        # sum_prb_avg,
        # cnt_prb_avg,
        prbusage_mean,
    ]

    # where
    ## 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(model_tbl.base_date, start_date, end_date))

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(model_tbl.mkng_cmpn_nm.in_(where_ins))
        code_column = model_tbl.mkng_cmpn_nm

    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부", "") for txt in where_ins]
        stmt_where_and.append(model_tbl.new_hq_nm.in_(where_ins))
        code_column = model_tbl.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터", "") for txt in where_ins]
        stmt_where_and.append(model_tbl.new_center_nm.in_(where_ins))
        code_column = model_tbl.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(model_tbl.oper_team_nm.in_(where_ins))
        code_column = model_tbl.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(model_tbl.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(model_tbl.area_jo_nm.in_(where_ins))
        code_column = model_tbl.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(model_tbl.sido_nm.in_(where_ins))
        code_column = model_tbl.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(model_tbl.gun_gu_nm.in_(where_ins))
        code_column = model_tbl.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(model_tbl.eup_myun_dong_nm.in_(where_ins))
        code_column = model_tbl.eup_myun_dong_nm

    elif code == "전국" or code =="전체" or code == "all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx
    
    # groupby :  rrc는 상품조건 없어, code_column으로 고정
    by_column = code_column
    # stmt 생성
    stmt = select(
        by_column.label("code"),
        model_tbl.base_date.label("date"),
        *entities,
    ).where(
        and_(*stmt_where_and)
    ).group_by(model_tbl.base_date,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.RrcTrendOutput(**dict(zip(query_keys, r))) for r in query_result if r[0] == code]
        list_items.append(schemas.RrcTrendItemOutput(title=code, data=t_l))

    return list_items



#####
async def get_rrc_trend_by_group_month(db: AsyncSession, code:str, group:str, start_month:str = None, end_month: str = None):
    sum_rrc_try = func.sum(func.ifnull(models.RrcTrendMM.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.RrcTrendMM.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.RrcTrendMM.prb_avg) * 100, 4).label("prbusage_mean")

    entities = [
        models.RrcTrendMM.base_ym.label("date"),
    ]
    entities_groupby = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_month:
        end_month = start_month

    if start_month:
        stmt = stmt.where(between(models.RrcTrendMM.base_ym, start_month, end_month))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.RrcTrendMM.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt = stmt.where(models.RrcTrendMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.RrcTrendMM.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.RrcTrendMM.oper_team_nm.in_(txt_l))
    elif code == "조별":
        stmt = stmt.where(models.RrcTrendMM.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.RrcTrendMM.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt = stmt.where(models.RrcTrendMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt = stmt.where(models.RrcTrendMM.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt = stmt.where(models.RrcTrendMM.eup_myun_dong_nm.in_(txt_l))
    elif code =="전국" or code =="전체" or code =="all": # 전국
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(models.RrcTrendMM.base_ym.asc())
    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_rrc_trend = list(map(lambda x: schemas.RrcTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_rrc_trend


async def get_rrc_trend_item_by_group_month(db: AsyncSession, code:str, group:str,
                                            start_month:str = None, end_month: str = None):
    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    sum_rrc_try = func.sum(func.ifnull(models.RrcTrendMM.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.RrcTrendMM.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.RrcTrendMM.prb_avg) * 100, 4).label("prbusage_mean")

    entities = [
        sum_rrc_try,
        sum_rrc_suc,
        rrc_rate,
        prbusage_mean,
    ]

    # where
    ## 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    stmt_where_and.append(between(models.RrcTrendMM.base_ym, start_month, end_month))

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.RrcTrendMM.mkng_cmpn_nm.in_(where_ins))
        code_column = models.RrcTrendMM.mkng_cmpn_nm

    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        stmt_where_and.append(models.RrcTrendMM.new_hq_nm.in_(where_ins))
        code_column = models.RrcTrendMM.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        stmt_where_and.append(models.RrcTrendMM.new_center_nm.in_(where_ins))
        code_column = models.RrcTrendMM.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(models.RrcTrendMM.oper_team_nm.in_(where_ins))
        code_column = models.RrcTrendMM.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(models.RrcTrendMM.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.RrcTrendMM.area_jo_nm.in_(where_ins))
        code_column = models.RrcTrendMM.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(models.RrcTrendMM.sido_nm.in_(where_ins))
        code_column = models.RrcTrendMM.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(models.RrcTrendMM.gun_gu_nm.in_(where_ins))
        code_column = models.RrcTrendMM.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(models.RrcTrendMM.eup_myun_dong_nm.in_(where_ins))
        code_column = models.RrcTrendMM.eup_myun_dong_nm

    elif code == "전국" or code == "전체" or code == "all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx

    # group by : rrc는 상품선택이 없어, code_column으로 고정
    by_column = code_column

    # stmt 생성
    stmt = select(
        by_column.label("code"),
        models.RrcTrendMM.base_ym.label("date"),
        *entities,
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.RrcTrendMM.base_ym,
               by_column)

    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.RrcTrendOutput(**dict(zip(query_keys, r))) for r in query_result if r[0] == code]
        list_items.append(schemas.RrcTrendItemOutput(title=code, data=t_l))

    return list_items