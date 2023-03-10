from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_, or_, literal
from datetime import datetime, timedelta

from app.utils.query_utils import band_to_equipcd2

async def get_mdt_trend_by_group_date(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None):
    sum_rsrp_m105d_cnt = func.sum(models.Mdt.rsrp_m105d_cnt)
    sum_rsrp_m110d_cnt = func.sum(models.Mdt.rsrp_m110d_cnt)
    sum_rsrp_cnt = func.sum(models.Mdt.rsrp_cnt)
    sum_rsrp_value = func.sum(models.Mdt.rsrp_sum)

    sum_rsrq_m15d_cnt = func.sum(models.Mdt.rsrq_m15d_cnt)
    sum_rsrq_m17d_cnt = func.sum(models.Mdt.rsrq_m17d_cnt)
    sum_rsrq_cnt = func.sum(models.Mdt.rsrq_cnt)
    sum_rsrq_value = func.sum(models.Mdt.rsrq_sum)

    sum_rip_maxd_cnt = func.sum(models.Mdt.new_rip_maxd_cnt)
    sum_rip_cnt = func.sum(models.Mdt.rip_cnt)
    sum_rip_value = func.sum(models.Mdt.rip_sum)

    sum_new_phr_m3d_cnt = func.sum(models.Mdt.new_phr_m3d_cnt)
    sum_new_phr_mind_cnt_cnt = func.sum(models.Mdt.new_phr_mind_cnt)
    sum_phr_cnt = func.sum(models.Mdt.phr_cnt)
    sum_phr_value = func.sum(models.Mdt.phr_sum)

    sum_nr_rsrp_cnt = func.sum(models.Mdt.nr_rsrp_cnt)
    sum_nr_rsrp_value = func.sum(models.Mdt.nr_rsrp_sum)

    rsrp_bad_rate = func.round((sum_rsrp_m105d_cnt + sum_rsrp_m110d_cnt) / (sum_rsrp_cnt + 1e-6) * 100, 4).label("rsrp_bad_rate")
    rsrp_mean = func.round(sum_rsrp_value / (sum_rsrp_cnt + 1e-6),4).label("rsrp_mean")

    rsrq_bad_rate = func.round((sum_rsrq_m15d_cnt + sum_rsrq_m17d_cnt) / (sum_rsrq_cnt + 1e-6) * 100,4).label("rsrq_bad_rate")
    rsrq_mean = func.round((sum_rsrq_value / (sum_rsrq_cnt + 1e-6)), 4).label("rsrq_mean")

    rip_bad_rate = func.round((sum_rip_maxd_cnt) / (sum_rip_cnt + 1e-6) * 100, 4).label("rip_bad_rate")
    rip_mean = func.round((sum_rip_value / (sum_rip_cnt + 1e-6)),4).label("rip_mean")

    phr_bad_rate = func.round((sum_new_phr_m3d_cnt + sum_new_phr_mind_cnt_cnt) / (sum_phr_cnt + 1e-6) * 100, 4).label("phr_bad_rate")
    phr_mean = func.round((sum_phr_value / (sum_phr_cnt + 1e-6)),4).label("phr_mean")

    nr_rsrp_mean = func.round((sum_nr_rsrp_value / (sum_nr_rsrp_cnt + 1e-6)),4).label("nr_rsrp_mean")

    entities = [
        models.Mdt.base_date.label("date"),
    ]
    entities_groupby = [
        rsrp_bad_rate,
        rsrp_mean,
        rsrq_bad_rate,
        rsrq_mean,
        rip_bad_rate,
        rip_mean,
        phr_bad_rate,
        phr_mean,
        nr_rsrp_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Mdt.base_date, start_date, end_date))

    txt_l = []
    # code??? ????????? : ??????|?????????
    if group != "":
        txt_l = group.split("|")

    # ?????? ??????
    if code == "????????????":
        stmt = stmt.where(models.Mdt.bts_maker_nm.in_(txt_l))
    elif code == "?????????":
        txt_l = [txt.replace("NW????????????","") for txt in txt_l]
        stmt = stmt.where(models.Mdt.new_hq_nm.in_(txt_l))
    elif code == "?????????":
        txt_l = [txt.replace("?????????????????????","") for txt in txt_l]
        stmt = stmt.where(models.Mdt.new_center_nm.in_(txt_l))
    elif code == "??????":
        stmt = stmt.where(models.Mdt.oper_team_nm.in_(txt_l))
    elif code == "??????":
        stmt = stmt.where(models.Mdt.area_jo_nm.in_(txt_l))
    elif code == "?????????":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "????????????":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "????????????":
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(txt_l))
    elif code == "??????" or code =="??????" or code == "all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.group_by(*entities).order_by(models.Mdt.base_date.asc())
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_mdt_trend = list(map(lambda x: schemas.MdtTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_mdt_trend


async def get_worst10_mdt_bts_by_group_date(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None,
                                        band: str=None, limit: int = 10):
    sum_rsrp_m105d_cnt = func.sum(models.Mdt.rsrp_m105d_cnt)
    sum_rsrp_m110d_cnt = func.sum(models.Mdt.rsrp_m110d_cnt)
    sum_rsrp_bad_cnt = (sum_rsrp_m105d_cnt + sum_rsrp_m110d_cnt).label("rsrp_bad_cnt")
    sum_rsrp_cnt = func.sum(models.Mdt.rsrp_cnt).label("rsrp_cnt")
    sum_rsrp_value = func.sum(models.Mdt.rsrp_sum)

    sum_rsrq_m15d_cnt = func.sum(models.Mdt.rsrq_m15d_cnt)
    sum_rsrq_m17d_cnt = func.sum(models.Mdt.rsrq_m17d_cnt)
    sum_rsrq_cnt = func.sum(models.Mdt.rsrq_cnt)
    sum_rsrq_value = func.sum(models.Mdt.rsrq_sum)

    sum_rip_maxd_cnt = func.sum(models.Mdt.new_rip_maxd_cnt)
    sum_rip_cnt = func.sum(models.Mdt.rip_cnt)
    sum_rip_value = func.sum(models.Mdt.rip_sum)

    sum_new_phr_m3d_cnt = func.sum(models.Mdt.new_phr_m3d_cnt)
    sum_new_phr_mind_cnt_cnt = func.sum(models.Mdt.new_phr_mind_cnt)
    sum_phr_cnt = func.sum(models.Mdt.phr_cnt)
    sum_phr_value = func.sum(models.Mdt.phr_sum)

    sum_nr_rsrp_cnt = func.sum(models.Mdt.nr_rsrp_cnt)
    sum_nr_rsrp_value = func.sum(models.Mdt.nr_rsrp_sum)

    rsrp_bad_rate = func.round(sum_rsrp_bad_cnt / (sum_rsrp_cnt + 1e-6) * 100, 4).\
        label("rsrp_bad_rate")
    rsrp_mean = func.round(sum_rsrp_value / (sum_rsrp_cnt + 1e-6),4).label("rsrp_mean")

    rsrq_bad_rate = func.round((sum_rsrq_m15d_cnt + sum_rsrq_m17d_cnt) / (sum_rsrq_cnt + 1e-6) * 100,4).\
        label("rsrq_bad_rate")
    rsrq_mean = func.round((sum_rsrq_value / (sum_rsrq_cnt + 1e-6)), 4).label("rsrq_mean")

    rip_bad_rate = func.round((sum_rip_maxd_cnt) / (sum_rip_cnt + 1e-6) * 100, 4).label("rip_bad_rate")
    rip_mean = func.round((sum_rip_value / (sum_rip_cnt + 1e-6)),4).label("rip_mean")

    phr_bad_rate = func.round((sum_new_phr_m3d_cnt + sum_new_phr_mind_cnt_cnt) / (sum_phr_cnt + 1e-6) * 100, 4).\
        label("phr_bad_rate")
    phr_mean = func.round((sum_phr_value / (sum_phr_cnt + 1e-6)),4).label("phr_mean")

    nr_rsrp_mean = func.round((sum_nr_rsrp_value / (sum_nr_rsrp_cnt + 1e-6)),4).label("nr_rsrp_mean")

    juso = func.concat(models.Mdt.gun_gu_nm+' ', models.Mdt.eup_myun_dong_nm).label("juso")

    entities = [
        models.Mdt.equip_cd.label("equip_cd"),
        models.Mdt.equip_nm.label("equip_nm"),
        # juso,
        # models.Mdt.area_center_nm.label("center"),
        # models.Mdt.oper_team_nm.label("team"),
        models.Mdt.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        rsrp_bad_rate,
        sum_rsrp_bad_cnt,
        sum_rsrp_cnt,
        rsrq_bad_rate,
        rip_bad_rate,
        phr_bad_rate,
        nr_rsrp_mean,
        rsrp_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Mdt.base_date, start_date, end_date))

    txt_l = []
    # code??? ????????? : ??????|?????????
    if group != "":
        txt_l = group.split("|")

    # ?????? ??????
    if code == "????????????":
        stmt = stmt.where(models.Mdt.bts_maker_nm.in_(txt_l))
    elif code == "?????????":
        txt_l = [txt.replace("NW????????????","") for txt in txt_l]
        stmt = stmt.where(models.Mdt.new_hq_nm.in_(txt_l))
    elif code == "?????????":
        txt_l = [txt.replace("?????????????????????","") for txt in txt_l]
        stmt = stmt.where(models.Mdt.new_center_nm.in_(txt_l))
    elif code == "??????":
        stmt = stmt.where(models.Mdt.oper_team_nm.in_(txt_l))
    elif code == "??????":
        stmt = stmt.where(models.Mdt.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.oper_team_nm != "???????????????????????????")
    elif code == "?????????":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "????????????":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "????????????":
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(txt_l))
    elif code == "??????" or code =="??????" or code == "all": # ??????
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # ??????????????? ??????
    if band :
        equipcd2 = band_to_equipcd2(band)
        stmt = stmt.where(func.substring(models.Mdt.equip_cd,1,2).in_(equipcd2))

    # stmt = stmt.group_by(*entities).having(sum_rsrp_cnt > 0).order_by(rsrp_bad_rate.desc()).subquery()
    stmt = stmt.where(models.Mdt.area_jo_nm!='?????????')
    stmt = stmt.group_by(*entities).having(sum_rsrp_cnt > 0).order_by(rsrp_bad_rate.desc()).limit(limit)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_mdt_bts = list(map(lambda x: schemas.MdtBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_mdt_bts


async def get_mdt_trend_item_by_group_date(db: AsyncSession, code:str, group: str,
                                           start_date: str = None, end_date: str = None):

    where_ins = []  # code?????????, volte ????????? where in (a, b, c)
    stmt_where_and = []  # where list

    # ????????????
    sum_rsrp_m105d_cnt = func.sum(models.Mdt.rsrp_m105d_cnt)
    sum_rsrp_m110d_cnt = func.sum(models.Mdt.rsrp_m110d_cnt)
    sum_rsrp_cnt = func.sum(models.Mdt.rsrp_cnt)
    sum_rsrp_value = func.sum(models.Mdt.rsrp_sum)

    sum_rsrq_m15d_cnt = func.sum(models.Mdt.rsrq_m15d_cnt)
    sum_rsrq_m17d_cnt = func.sum(models.Mdt.rsrq_m17d_cnt)
    sum_rsrq_cnt = func.sum(models.Mdt.rsrq_cnt)
    sum_rsrq_value = func.sum(models.Mdt.rsrq_sum)

    sum_rip_maxd_cnt = func.sum(models.Mdt.new_rip_maxd_cnt)
    sum_rip_cnt = func.sum(models.Mdt.rip_cnt)
    sum_rip_value = func.sum(models.Mdt.rip_sum)

    sum_new_phr_m3d_cnt = func.sum(models.Mdt.new_phr_m3d_cnt)
    sum_new_phr_mind_cnt_cnt = func.sum(models.Mdt.new_phr_mind_cnt)
    sum_phr_cnt = func.sum(models.Mdt.phr_cnt)
    sum_phr_value = func.sum(models.Mdt.phr_sum)

    sum_nr_rsrp_cnt = func.sum(models.Mdt.nr_rsrp_cnt)
    sum_nr_rsrp_value = func.sum(models.Mdt.nr_rsrp_sum)

    rsrp_bad_rate = func.round((sum_rsrp_m105d_cnt + sum_rsrp_m110d_cnt) / (sum_rsrp_cnt + 1e-6) * 100, 4). \
        label("rsrp_bad_rate")
    rsrp_mean = func.round(sum_rsrp_value / (sum_rsrp_cnt + 1e-6), 4).label("rsrp_mean")

    rsrq_bad_rate = func.round((sum_rsrq_m15d_cnt + sum_rsrq_m17d_cnt) / (sum_rsrq_cnt + 1e-6) * 100, 4). \
        label("rsrq_bad_rate")
    rsrq_mean = func.round((sum_rsrq_value / (sum_rsrq_cnt + 1e-6)), 4).label("rsrq_mean")

    rip_bad_rate = func.round((sum_rip_maxd_cnt) / (sum_rip_cnt + 1e-6) * 100, 4).label("rip_bad_rate")
    rip_mean = func.round((sum_rip_value / (sum_rip_cnt + 1e-6)), 4).label("rip_mean")

    phr_bad_rate = func.round((sum_new_phr_m3d_cnt + sum_new_phr_mind_cnt_cnt) / (sum_phr_cnt + 1e-6) * 100, 4). \
        label("phr_bad_rate")
    phr_mean = func.round((sum_phr_value / (sum_phr_cnt + 1e-6)), 4).label("phr_mean")

    nr_rsrp_mean = func.round((sum_nr_rsrp_value / (sum_nr_rsrp_cnt + 1e-6)), 4).label("nr_rsrp_mean")

    entities = [
        rsrp_bad_rate,
        rsrp_mean,
        rsrq_bad_rate,
        rsrq_mean,
        rip_bad_rate,
        rip_mean,
        phr_bad_rate,
        phr_mean,
        nr_rsrp_mean
    ]
    # where
    ## ????????????
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Mdt.base_date, start_date, end_date))

    ## code??? ????????? : ??????|?????????
    if group != "":
        where_ins = group.split("|")

    ## ?????? ??????
    if code == "????????????":
        stmt_where_and.append(models.Mdt.mkng_cmpn_nm.in_(where_ins))
        code_column = models.Mdt.mkng_cmpn_nm

    elif code == "?????????":
        where_ins = [txt.replace("NW????????????","") for txt in where_ins]
        stmt_where_and.append(models.Mdt.new_hq_nm.in_(where_ins))
        code_column = models.Mdt.new_hq_nm

    elif code == "?????????":
        where_ins = [txt.replace("?????????????????????","") for txt in where_ins]
        stmt_where_and.append(models.Mdt.new_center_nm.in_(where_ins))
        code_column = models.Mdt.new_center_nm

    elif code == "??????":
        stmt_where_and.append(models.Mdt.oper_team_nm.in_(where_ins))
        code_column = models.Mdt.oper_team_nm

    elif code == "??????":
        stmt_where_and.append(models.Mdt.oper_team_nm != "???????????????????????????")
        stmt_where_and.append(models.Mdt.area_jo_nm.in_(where_ins))
        code_column = models.Mdt.area_jo_nm

    elif code == "?????????":
        stmt_where_and.append(models.Mdt.sido_nm.in_(where_ins))
        code_column = models.Mdt.sido_nm

    elif code == "????????????":
        stmt_where_and.append(models.Mdt.gun_gu_nm.in_(where_ins))
        code_column = models.Mdt.gun_gu_nm

    elif code == "????????????":
        stmt_where_and.append(models.Mdt.eup_myun_dong_nm.in_(where_ins))
        code_column = models.Mdt.eup_myun_dong_nm

    elif code == "??????" or code =="??????" or code =="all":
        code_column = literal("all")
    else:
        raise ex.NotFoundAccessKeyEx

    #group by (mdt??? ??????????????? ????????? code_column?????? ????????????)
    by_column = code_column

    #stmt ??????
    stmt = select(
        by_column.label("code"),
        models.Mdt.base_date.label("date"),
        *entities
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.Mdt.base_date,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.MdtTrendOutput(**dict(zip(query_keys, r))) for r in query_result if r[0] == code]
        list_items.append(schemas.MdtTrendItemOutput(title=code, data=t_l))

    return list_items

