from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_
from datetime import datetime, timedelta


async def get_mdt_trend_by_group_date2(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None):
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
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_cut = stmt.where(models.Mdt.bts_maker_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Mdt.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.Mdt.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Mdt.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.Mdt.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Mdt.oper_team_nm != "지하철엔지니어링부")

    elif code == "조별":
        stmt = stmt.where(models.Mdt.area_jo_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(models.Mdt.base_date.asc())

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_mdt_trend = list(map(lambda x: schemas.MdtTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_mdt_trend


async def get_worst10_mdt_bts_by_group_date2(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None,
                                        limit: int = 10):
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

    # juso = func.concat(models.Mdt.sido_nm+' ', models.Mdt.eup_myun_dong_nm).label("juso")

    entities = [
        models.Mdt.equip_cd.label("equip_cd"),
        models.Mdt.equip_nm.label("equip_nm"),
        # juso,
        models.Mdt.area_center_nm.label("center"),
        models.Mdt.oper_team_nm.label("team"),
        models.Mdt.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        rsrp_bad_rate,
        sum_rsrp_bad_cnt,
        sum_rsrp_cnt,
        rsrq_bad_rate,
        rip_bad_rate,
        phr_bad_rate,
        nr_rsrp_mean
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.Mdt.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_cut = stmt.where(models.Mdt.bts_maker_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Mdt.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.Mdt.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Mdt.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.Mdt.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Mdt.oper_team_nm != "지하철엔지니어링부")

    elif code == "조별":
        stmt = stmt.where(models.Mdt.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(models.AddrCode.eup_myun_dong_nm).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.Mdt.eup_myun_dong_nm.in_(txt_l))
    else: # 전국
        pass

    # stmt = stmt.group_by(*entities).having(sum_rsrp_cnt > 0).order_by(rsrp_bad_rate.desc()).subquery()
    stmt = stmt.where(models.Mdt.area_jo_nm!='값없음')
    stmt = stmt.group_by(*entities).having(sum_rsrp_cnt > 0).order_by(rsrp_bad_rate.desc()).limit(limit)

    stmt_rk = select([
        func.rank().over(order_by=stmt.c.rsrp_bad_rate.desc()).label("RANK"),
        *stmt.c
    ])

    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    list_worst_mdt_bts = list(map(lambda x: schemas.MdtBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_mdt_bts


async def get_mdt_trend_item_by_group_date(db: AsyncSession, code:str, group: str, start_date: str = None, end_date: str = None):
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

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

    # 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Mdt.base_date, start_date, end_date))

    # code의 값목록 : 삼성|노키아
    if group != "":
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_sel_nm = models.Mdt.bts_maker_nm
    elif code == "본부별":
        code_tbl_nm = select(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).\
                    group_by(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).subquery()
        code_sel_nm = code_tbl_nm.c.biz_hq_nm
        code_where_nm = code_tbl_nm.c.bonbu_nm

        stmt_sel_nm = models.Mdt.biz_hq_nm
    elif code == "센터별":
        # code_tbl_nm = models.OrgCode
        # code_sel_nm = models.OrgCode.area_jo_nm
        # code_where_nm = models.OrgCode.biz_hq_nm

        stmt_sel_nm = models.Mdt.biz_hq_nm
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in where_ins:
            stmt_sel_nm = models.Mdt.oper_team_nm
        else:
            code_tbl_nm = select(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm). \
                group_by(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm).subquery()
            code_sel_nm = code_tbl_nm.c.area_jo_nm
            code_where_nm = code_tbl_nm.c.oper_team_nm

            stmt_sel_nm = models.Mdt.area_jo_nm
            stmt_where_and.append(models.Mdt.oper_team_nm != "지하철엔지니어링부")

    elif code == "조별":
        stmt_sel_nm = models.Mdt.area_jo_nm
        stmt_where_and.append(models.Mdt.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.sido_nm

        stmt_sel_nm = models.Mdt.eup_myun_dong_nm
    elif code == "시군구별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.gun_gu_nm

        stmt_sel_nm = models.Mdt.eup_myun_dong_nm
    elif code == "읍면동별":
        stmt_sel_nm = models.Mdt.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if code_tbl_nm == None:  # code table 미사용시
        stmt_where_and.append(stmt_sel_nm.in_(where_ins))

        stmt = select(
            stmt_sel_nm.label("code"),
            models.Mdt.base_date.label("date"),
            rsrp_bad_rate,
            rsrp_mean,
            rsrq_bad_rate,
            rsrq_mean,
            rip_bad_rate,
            rip_mean,
            phr_bad_rate,
            phr_mean,
            nr_rsrp_mean
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Mdt.base_date, stmt_sel_nm)

    else:  # code table 사용시
        stmt_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        stmt_where_and.append(stmt_sel_nm.in_(stmt_wh))

        st_in = select(
            stmt_sel_nm.label("code"),
            models.Mdt.base_date,
            sum_rsrp_m105d_cnt.label("sum_rsrp_m105d_cnt"),
            sum_rsrp_m110d_cnt.label("sum_rsrp_m110d_cnt"),
            sum_rsrp_cnt.label("sum_rsrp_cnt"),
            sum_rsrp_value.label("sum_rsrp_value"),
            sum_rsrq_m15d_cnt.label("sum_rsrq_m15d_cnt"),
            sum_rsrq_m17d_cnt.label("sum_rsrq_m17d_cnt"),
            sum_rsrq_cnt.label("sum_rsrq_cnt"),
            sum_rsrq_value.label("sum_rsrq_value"),
            sum_rip_maxd_cnt.label("sum_rip_maxd_cnt"),
            sum_rip_cnt.label("sum_rip_cnt"),
            sum_rip_value.label("sum_rip_value"),
            sum_new_phr_m3d_cnt.label("sum_new_phr_m3d_cnt"),
            sum_new_phr_mind_cnt_cnt.label("sum_new_phr_mind_cnt_cnt"),
            sum_phr_cnt.label("sum_phr_cnt"),
            sum_phr_value.label("sum_phr_value"),
            sum_nr_rsrp_value.label("sum_nr_rsrp_value"),
            sum_nr_rsrp_cnt.label("sum_nr_rsrp_cnt")
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Mdt.base_date, stmt_sel_nm)

        stmt = select(
            code_where_nm.label("code"),
            st_in.c.base_date.label("date"),
            func.round((func.sum(st_in.c.sum_rsrp_m105d_cnt) + func.sum(st_in.c.sum_rsrp_m110d_cnt)) /
                       (func.sum(st_in.c.sum_rsrp_cnt) + 1e-6) * 100, 4).label("rsrp_bad_rate"),
            func.round(func.sum(st_in.c.sum_rsrp_value) /
                       (func.sum(st_in.c.sum_rsrp_cnt) + 1e-6), 4).label("rsrp_mean"),
            func.round((func.sum(st_in.c.sum_rsrq_m15d_cnt) + func.sum(st_in.c.sum_rsrq_m17d_cnt)) /
                       (func.sum(st_in.c.sum_rsrq_cnt) + 1e-6) * 100, 4).label("rsrq_bad_rate"),
            func.round((func.sum(st_in.c.sum_rsrq_value) /
                        (func.sum(st_in.c.sum_rsrq_cnt) + 1e-6)), 4).label("rsrq_mean"),
            func.round(func.sum(st_in.c.sum_rip_maxd_cnt) /
                       (func.sum(st_in.c.sum_rip_cnt) + 1e-6) * 100, 4).label("rip_bad_rate"),
            func.round((func.sum(st_in.c.sum_rip_value) /
                        (func.sum(st_in.c.sum_rip_cnt) + 1e-6)), 4).label("rip_mean"),
            func.round((func.sum(st_in.c.sum_new_phr_m3d_cnt) + func.sum(st_in.c.sum_new_phr_mind_cnt_cnt)) /
                       (func.sum(st_in.c.sum_phr_cnt) + 1e-6) * 100, 4).label("phr_bad_rate"),
            func.round((func.sum(st_in.c.sum_phr_value) /
                        (func.sum(st_in.c.sum_phr_cnt) + 1e-6)), 4).label("phr_mean"),
            func.round((func.sum(st_in.c.sum_nr_rsrp_value) /
                        (func.sum(st_in.c.sum_nr_rsrp_cnt) + 1e-6)), 4).label("nr_rsrp_mean")
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in.c.code
        ).group_by(
            st_in.c.base_date,
            code_where_nm
        )

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.MdtTrendOutput(**dict(zip(query_keys, r))) for r in query_result if r[0] == code]
        list_items.append(schemas.MdtTrendItemOutput(title=code, data=t_l))

    return list_items

