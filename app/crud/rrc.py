from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_
from datetime import datetime, timedelta


async def get_rrc_trend_by_group_date2(db: AsyncSession, code:str, group:str, start_date:str = None, end_date: str = None):
    sum_rrc_try = func.sum(func.ifnull(models.Rrc.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.Rrc.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prb_avg) * 100, 4).label("prbusage_mean")

    entities = [
        models.Rrc.base_date.label("date"),
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
        stmt = stmt.where(between(models.Rrc.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Rrc.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Rrc.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        stmt = stmt.where(models.Rrc.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Rrc.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.Rrc.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Rrc.oper_team_nm != "지하철엔지니어링부")
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
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(models.Rrc.base_date.asc())
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_rrc_trend = list(map(lambda x: schemas.RrcTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_rrc_trend


async def get_worst10_rrc_bts_by_group_date2(db: AsyncSession, prod:str, code:str, group: str,
                                             start_date: str = None, end_date: str = None, limit: int = 10):
    sum_rrc_try = func.sum(func.ifnull(models.Rrc.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.Rrc.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prb_avg) * 100, 4).label("prbusage_mean")

    entities = [
        models.Rrc.equip_cd.label("equip_cd"),
        models.Rrc.equip_nm.label("equip_nm"),
        # juso,
        models.Rrc.area_center_nm.label("center"),
        models.Rrc.oper_team_nm.label("team"),
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
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Rrc.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        stmt = stmt.where(models.Rrc.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Rrc.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.Rrc.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Rrc.oper_team_nm != "지하철엔지니어링부")
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
    else: # 전국
        pass

    #worst 기준(RRC성공률, 트래픽, PRB부하율)
    if prod == "RRC성공률":
        order_col = rrc_rate.asc()
    elif prod == "트래픽":
        order_col = sum_rrc_try.desc()
    elif prod == "PRB부하율":
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
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    sum_rrc_try = func.sum(func.ifnull(models.Rrc.rrc_att_sum, 0.0)).label("rrc_try")
    sum_rrc_suc = func.sum(func.ifnull(models.Rrc.rrc_suces_sum, 0.0)).label("rrc_suc")
    rrc_rate = func.round(sum_rrc_suc / (sum_rrc_try + 1e-6) * 100, 4).label("rrc_rate")
    prbusage_mean = func.round(func.avg(models.Rrc.prb_avg) * 100, 4).label("prbusage_mean")

    # 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.Rrc.base_date, start_date, end_date))

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_sel_nm = models.Rrc.mkng_cmpn_nm
    elif code == "본부별":
        code_tbl_nm = select(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).\
                    group_by(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).subquery()
        code_sel_nm = code_tbl_nm.c.biz_hq_nm
        code_where_nm = code_tbl_nm.c.bonbu_nm

        stmt_sel_nm = models.Rrc.biz_hq_nm
    elif code == "센터별":
        # code_tbl_nm = models.OrgCode
        # code_sel_nm = models.OrgCode.area_jo_nm
        # code_where_nm = models.OrgCode.biz_hq_nm
        #
        # stmt_sel_nm = models.Rrc.area_jo_nm
        stmt_sel_nm = models.Rrc.biz_hq_nm

    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in where_ins:
            stmt_sel_nm = models.Rrc.oper_team_nm
        else:
            code_tbl_nm = select(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm).\
                    group_by(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm).subquery()
            code_sel_nm = code_tbl_nm.c.area_jo_nm
            code_where_nm = code_tbl_nm.c.oper_team_nm

            stmt_sel_nm = models.Rrc.area_jo_nm
            stmt_where_and.append(models.Rrc.oper_team_nm != "지하철엔지니어링부")
    elif code == "조별":
        stmt_sel_nm = models.Rrc.area_jo_nm
        stmt_where_and.append(models.Rrc.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.sido_nm

        stmt_sel_nm = models.Rrc.eup_myun_dong_nm
    elif code == "시군구별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.gun_gu_nm

        stmt_sel_nm = models.Rrc.eup_myun_dong_nm
    elif code == "읍면동별":
        stmt_sel_nm = models.Rrc.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if code_tbl_nm == None:  # code table 미사용시
        stmt_where_and.append(stmt_sel_nm.in_(where_ins))

        stmt = select(
            stmt_sel_nm.label("code"),
            models.Rrc.base_date.label("date"),
            sum_rrc_try,
            # sum_rrc_suc,
            rrc_rate,
            prbusage_mean,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Rrc.base_date, stmt_sel_nm)

    else:  # code table 사용시
        stmt_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        stmt_where_and.append(stmt_sel_nm.in_(stmt_wh))

        st_in = select(
            stmt_sel_nm.label("code"),
            models.Rrc.base_date,
            sum_rrc_try,
            sum_rrc_suc,
            prbusage_mean,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.Rrc.base_date, stmt_sel_nm)

        stmt = select(
            code_where_nm.label("code"),
            st_in.c.base_date.label("date"),
            func.sum(st_in.c.rrc_try).label("rrc_try"),
            # func.sum(st_in.c.sum_rrc_suc).label("rrc_suc"),
            func.avg(st_in.c.prbusage_mean).label("prbusage_mean"),
            func.round(func.sum(st_in.c.rrc_suc) / (func.sum(st_in.c.rrc_try) + 1e-6) * 100, 4).label("rrc_rate"),
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in.c.code
        ).group_by(
            st_in.c.base_date,
            code_where_nm
        )
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

