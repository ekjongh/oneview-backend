from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from .. import schemas, models
from sqlalchemy import func, select, between, case, Column, and_
from datetime import datetime, timedelta

def date_range(start, end):
    start = datetime.strptime(start, '%Y%m%d')
    end = datetime.strptime(end, '%Y%m%d')
    dates = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range((end-start).days+1)]
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
        g5_off_ratio,
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data
    ]
    
    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        # base_date list 생성
        # stmt = stmt.where(between(models.Offloading_Bts.base_date, start_date, end_date))
        date_list = date_range(start_date, end_date)
        stmt = stmt.where(models.Offloading_Bts.base_date.in_(date_list))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.Offloading_Bts.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        # biz_hq_nm 조회 ->
        stmt_where= select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        query = await db.execute(stmt_where)
        query_result = query.all()
        orglist = [r[0] for r in query_result]

        # stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.biz_hq_nm.in_(stmt_where))
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm.in_(orglist))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # stmt = stmt.where(models.Offloading_Bts.oper_team_nm.in_(txt_l))
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Offloading_Bts.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).distinct().where(models.OrgCode.oper_team_nm.in_(txt_l))
            query = await db.execute(stmt_where)
            query_result = query.all()
            orglist = [r[0] for r in query_result]

            # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(orglist))
            stmt = stmt.where(models.Offloading_Bts.oper_team_nm != "지하철엔지니어링부")
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
    else: # 전국
        pass

    stmt = stmt.group_by(*entities).order_by(models.Offloading_Bts.base_date.asc())

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_offloading_trend


# worst주요단말(데이터량기준) : 조 기준 X,
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
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Hndset.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Hndset.oper_team_nm.in_(stmt_where))
        stmt = stmt.where(models.Offloading_Hndset.biz_hq_nm.in_(txt_l))
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
    else: # 전국
        pass

    #주요단말정렬기준 : 데이터량
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
        stmt_cut = stmt.where(models.Offloading_Bts.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(models.OrgCode.biz_hq_nm).distinct().where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm.in_(stmt_where))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
        stmt = stmt.where(models.Offloading_Bts.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # stmt = stmt.where(models.Offloading_Bts.oper_team_nm.in_(txt_l))
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.Offloading_Bts.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(models.OrgCode.area_jo_nm).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.Offloading_Bts.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.Offloading_Bts.oper_team_nm != "지하철엔지니어링부")
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
    else: # 전국
        pass

    # stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).subquery()
    stmt = stmt.where(models.Offloading_Bts.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).having(g5_off_ratio > 0).order_by(g5_off_ratio.asc()).limit(limit)

    stmt_rk = select([
        # func.rank().over(order_by=stmt.c.g5_off_ratio.asc()).label("RANK"),
        *stmt.c
    ]).order_by(stmt.c.g5_off_ratio.asc()).limit(limit)

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

    # stmt_where_and.append(between(models.Offloading_Bts.base_date, start_date, end_date))
    date_list = date_range(start_date, end_date)
    stmt_where_and.append(models.Offloading_Bts.base_date.in_(date_list))

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    # where 에 codetbl 조회결과...
    # 디비실행
    # orglist 사용시에는 끝에 추가.
    if code == "제조사별":
        stmt_where_and.append(models.Offloading_Bts.mkng_cmpn_nm.in_(where_ins))
        stmt_sel_nm = models.Offloading_Bts.mkng_cmpn_nm
    elif code == "본부별":
        # stmt_sel_nm = models.Offloading_Bts.biz_hq_nm
        stmt_where = select(models.OrgCode.bonbu_nm, models.OrgCode.biz_hq_nm).distinct().\
                where(models.OrgCode.bonbu_nm.in_(where_ins)).\
                order_by(models.OrgCode.bonbu_nm)
        query = await db.execute(stmt_where)
        query_result = query.all()

        # case_dict, suborg_list 생성
        case_dict, suborg_list = make_case_code(query_result)

        case_list = []
        for key in case_dict.keys():
            item = case_dict[key]
            case_list.append((models.Offloading_Bts.biz_hq_nm.in_(item), key))

        stmt_sel_nm = case(case_list).label("code")
        stmt_where_and.append(models.Offloading_Bts.biz_hq_nm.in_(suborg_list))
    elif code == "센터별":
        # code_tbl_nm = models.OrgCode
        # code_sel_nm = models.OrgCode.area_jo_nm
        # code_where_nm = models.OrgCode.biz_hq_nm

        stmt_sel_nm = models.Offloading_Bts.biz_hq_nm
        stmt_where_and.append(models.Offloading_Bts.biz_hq_nm.in_(where_ins))
    elif code == "팀별":
        # stmt_sel_nm = models.Offloading_Bts.oper_team_nm
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in where_ins:
            stmt_where_and.append(models.Offloading_Bts.oper_team_nm.in_(where_ins))
            stmt_sel_nm = models.Offloading_Bts.oper_team_nm
        else:
            stmt_where = select(models.OrgCode.oper_team_nm, models.OrgCode.area_jo_nm).distinct(). \
                where(models.OrgCode.oper_team_nm.in_(where_ins)). \
                order_by(models.OrgCode.oper_team_nm)
            query = await db.execute(stmt_where)
            query_result = query.all()

            # case_dict, suborg_list(jo목록) 생성
            case_dict, suborg_list = make_case_code(query_result)

            case_list = [] # case when jo in (1,2,3) then team,
            for key in case_dict.keys():
                item = case_dict[key]
                case_list.append((models.Offloading_Bts.area_jo_nm.in_(item), key))

            stmt_sel_nm = case(case_list).label("code")
            stmt_where_and.append(models.Offloading_Bts.area_jo_nm.in_(suborg_list))
            stmt_where_and.append(models.Offloading_Bts.oper_team_nm != "지하철엔지니어링부")
    elif code == "조별":
        stmt_sel_nm = models.Offloading_Bts.area_jo_nm
        stmt_where_and.append(models.Offloading_Bts.area_jo_nm.in_(where_ins))
        stmt_where_and.append(models.Offloading_Bts.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(models.AddrCode.sido_nm, models.AddrCode.eup_myun_dong_nm).distinct().\
                where(models.AddrCode.sido_nm.in_(where_ins)).\
                order_by(models.AddrCode.sido_nm)
        query = await db.execute(stmt_where)
        query_result = query.all()

        # case_dict, suborg_list 생성
        case_dict, suborg_list = make_case_code(query_result)

        case_list = []
        for key in case_dict.keys():
            item = case_dict[key]
            case_list.append((models.Offloading_Bts.eup_myun_dong_nm.in_(item), key))

        stmt_sel_nm = case(case_list).label("code")
        stmt_where_and.append(models.Offloading_Bts.eup_myun_dong_nm.in_(suborg_list))

    elif code == "시군구별":
        stmt_where = select(models.AddrCode.gun_gu_nm, models.AddrCode.eup_myun_dong_nm).distinct().\
                where(models.AddrCode.gun_gu_nm.in_(where_ins)).\
                order_by(models.AddrCode.gun_gu_nm)
        query = await db.execute(stmt_where)
        query_result = query.all()

        # case_dict, suborg_list 생성
        case_dict, suborg_list = make_case_code(query_result)

        case_list = []
        for key in case_dict.keys():
            item = case_dict[key]
            case_list.append((models.Offloading_Bts.eup_myun_dong_nm.in_(item), key))

        stmt_sel_nm = case(case_list).label("code")
        stmt_where_and.append(models.Offloading_Bts.eup_myun_dong_nm.in_(suborg_list))
    elif code == "읍면동별":
        stmt_where_and.append(models.Offloading_Bts.eup_myun_dong_nm.in_(where_ins))
        stmt_sel_nm = models.Offloading_Bts.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # db실행
    stmt = select(
        stmt_sel_nm.label("code"),
        models.Offloading_Bts.base_date.label("date"),
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio,
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.Offloading_Bts.base_date, stmt_sel_nm
    ).order_by()

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.OffloadingTrendOutput(**r) for r in query_result if r[0] == code]
        list_items.append(schemas.OffloadingTrendItemOutput(title=code, data=t_l))

    return list_items
