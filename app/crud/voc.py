from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from app import schemas
from sqlalchemy import func, select, between, case, and_, Column, distinct
from datetime import datetime, timedelta

from app import models


async def get_worst10_bts_by_group_date2(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                   start_date: str = None, end_date: str = None, limit: int = 10):
    # 기지국별 VOC Worst TOP 10
    voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no_cnt, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
    juso = func.concat(models.VocList.sido_nm+' ', models.VocList.eup_myun_dong_nm).label("juso")
    
    entities = [
        models.VocList.equip_cd,
        models.VocList.equip_nm,
        # juso,
        models.VocList.biz_hq_nm.label("center"),
        models.VocList.oper_team_nm.label("team"),
        models.VocList.area_jo_nm.label("jo")
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(*entities, *entities_groupby)

    # 기간 조건
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm == prod)

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(distinct(models.OrgCode.oper_team_nm)).where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.oper_team_nm.in_(stmt_where))
    elif code == "센터별":
        stmt = stmt.where(models.VocList.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # code_val = models.VocList.oper_team_nm
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.VocList.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(distinct(models.OrgCode.area_jo_nm)).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.VocList.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "조별":
        stmt = stmt.where(models.VocList.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(distinct(models.AddrCode.eup_myun_dong_nm)).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(distinct(models.AddrCode.eup_myun_dong_nm)).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(txt_l))
    else:
        pass

    stmt = stmt.where(models.VocList.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).limit(limit)
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    # stmt_rk = select([
    #     func.rank().over(order_by=stmt.c.voc_cnt.desc()).label('RANK'),
    #     *stmt.c,
    # ])

    # query = db.execute(stmt_rk)
    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_bts


async def get_worst10_hndset_by_group_date2(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                      start_date: str = None, end_date: str = None, limit: int = 10):
    # 단말별 품질 VOC Worst TOP10
    voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no_cnt, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
   
    entities = [
        models.VocList.hndset_pet_nm,
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(*entities, *entities_groupby)

    # 기간 조건
    if not end_date:
        end_date = start_date

    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))

    txt_l = []
    # code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm == prod)

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(distinct(models.OrgCode.oper_team_nm)).where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.oper_team_nm.in_(stmt_where))
    elif code == "센터별":
        stmt = stmt.where(models.VocList.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부 -> oper_team_nm 사용, 그외 -> area_team_nm && not 지하철
        if "지하철엔지니어링부" in txt_l:
            stmt = stmt.where(models.VocList.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(distinct(models.OrgCode.area_jo_nm)).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt = stmt.where(models.VocList.area_jo_nm.in_(stmt_where))
            stmt = stmt.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "조별":
        stmt = stmt.where(models.VocList.area_jo_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where = select(distinct(models.AddrCode.eup_myun_dong_nm)).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(stmt_where))
    elif code == "시군구별":
        stmt_where = select(distinct(models.AddrCode.eup_myun_dong_nm)).where(models.AddrCode.gun_gu_nm.in_(txt_l))
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(stmt_where))
    elif code == "읍면동별":
        stmt = stmt.where(models.VocList.eup_myun_dong_nm.in_(txt_l))
    else:
        code_val = None

    stmt = stmt.where(models.VocList.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).limit(limit)

    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_voc_hndset = list(map(lambda x: schemas.VocHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_hndset


async def get_voc_list_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                               limit: int = 1000):
    juso = models.VocList.trobl_rgn_broad_sido_nm + ' ' \
           + models.VocList.trobl_rgn_sgg_nm + ' ' \
           + models.VocList.trobl_rgn_eup_myun_dong_li_nm + ' ' \
           + models.VocList.trobl_rgn_dtl_sbst
    juso = juso.label("juso")

    entities = [
        models.VocList.base_date,       # label("기준년원일"),
        models.VocList.sr_tt_rcp_no,    # label("VOC접수번호"),
        models.VocList.voc_type_nm,     # label("VOC유형"),
        models.VocList.voc_wjt_scnd_nm,     # label("VOC2차업무유형"),
        models.VocList.voc_wjt_tert_nm,     # label("VOC3차업무유형"),
        models.VocList.voc_wjt_qrtc_nm,     # label("VOC4차업무유형"),
        models.VocList.svc_cont_id,     # label("서비스계약번호"),
        models.VocList.hndset_pet_nm,   # label("단말기명"),
        models.VocList.anals_3_prod_level_nm,   # label("분석상품레벨3"),
        models.VocList.bprod_nm,        # label("요금제"),
        models.VocList.equip_nm,        # label("주기지국"),
        models.VocList.biz_hq_nm,       # label("주기지국센터"),
        models.VocList.oper_team_nm,    # label("주기지국팀"),
        models.VocList.area_jo_nm,      # label("주기지국조")
        models.VocList.voc_rcp_txn,
        models.VocList.voc_actn_txn,
        models.VocList.tt_trt_sbst,
        juso,

    ]
    stmt = select(*entities)
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VocList.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.VocList.biz_hq_nm == group)
    elif group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.VocList.oper_team_nm == group)
    elif group.endswith("조"):
        stmt = stmt.where(models.VocList.area_jo_nm == group)
    # else:
    #     pass

    query = await db.execute(stmt)
    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()
    list_voc_list = list(map(lambda x: schemas.VocListOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_list


async def get_voc_trend_by_group_date2(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                 start_date: str = None, end_date: str = None):
    # 1000가입자당  VOC건수
    voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no_cnt, 0)).label("value")

    stmt_voc = select(models.VocList.base_date.label("date"), voc_cnt)

    # 기간
    if not end_date:
        end_date = start_date

    if start_date:
        stmt_voc = stmt_voc.where(between(models.VocList.base_date, start_date, end_date))

    txt_l = []
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_voc = stmt_voc.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        stmt_where = select(distinct(models.OrgCode.oper_team_nm)).where(models.OrgCode.bonbu_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm.in_(stmt_where))
    elif code == "센터별":
        stmt_voc = stmt_voc.where(models.VocList.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in txt_l:
            stmt_voc = stmt_voc.where(models.VocList.oper_team_nm.in_(txt_l))
        else:
            stmt_where = select(distinct(models.OrgCode.area_jo_nm)).where(models.OrgCode.oper_team_nm.in_(txt_l))
            stmt_voc = stmt_voc.where(models.VocList.area_jo_nm.in_(stmt_where))
            stmt_voc = stmt_voc.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code== "조별":
        stmt_voc = stmt_voc.where(models.VocList.area_jo_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_voc = stmt_voc.where(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_voc = stmt_voc.where(models.VocList.gun_gu_nm.in_(txt_l))
    else:
        pass

    # 상품 조건
    if prod and prod != "전체":
        stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm == prod)

    stmt_voc = stmt_voc.where(models.VocList.area_jo_nm != "값없음")
    stmt_voc = stmt_voc.group_by(models.VocList.base_date).order_by(models.VocList.base_date.asc())



    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend



async def get_voc_spec_by_srno(db: AsyncSession, sr_tt_rcp_no: str = "", limit: int = 1000):
    # 1. voc상세
    juso = models.VocList.trobl_rgn_broad_sido_nm + ' ' \
           + models.VocList.trobl_rgn_sgg_nm + ' ' \
           + models.VocList.trobl_rgn_eup_myun_dong_li_nm + ' ' \
           + models.VocList.trobl_rgn_dtl_sbst
    juso = juso.label("juso")

    entities_voc = [
        models.VocList.base_date,  # label("기준년원일"),
        models.VocList.sr_tt_rcp_no,  # label("VOC접수번호"),
        models.VocList.voc_type_nm,  # label("VOC유형"),
        models.VocList.voc_wjt_scnd_nm,  # label("VOC2차업무유형"),
        models.VocList.voc_wjt_tert_nm,  # label("VOC3차업무유형"),
        models.VocList.voc_wjt_qrtc_nm,  # label("VOC4차업무유형"),
        models.VocList.svc_cont_id,  # label("서비스계약번호"),
        models.VocList.hndset_pet_nm,  # label("단말기명"),
        models.VocList.anals_3_prod_level_nm,  # label("분석상품레벨3"),
        models.VocList.bprod_nm,  # label("요금제"),
        models.VocList.sr_tt_rcp_no,
        models.VocList.svc_cont_id,
        juso,
        models.VocList.voc_rcp_txn,
        models.VocList.voc_actn_txn,
        models.VocList.tt_trt_sbst,
        models.VocList.equip_cd,
        models.VocList.equip_nm,
        models.VocList.latit_val,
        models.VocList.lngit_val,
        models.VocList.biz_hq_nm,  # label("주기지국센터"),
        models.VocList.oper_team_nm,  # label("주기지국팀"),
        models.VocList.area_jo_nm,  # label("주기지국조")
        models.VocList.utmkx,
        models.VocList.utmky,
        models.VocList.day_utmkx,
        models.VocList.day_utmky,
        models.VocList.ngt_utmkx,
        models.VocList.ngt_utmky,
        models.VocList.equip_cd_data,
        models.VocList.equip_nm_data,
        models.VocList.latit_val_data,
        models.VocList.lngit_val_data,
    ]
    stmt_voc = select(*entities_voc).where(models.VocList.sr_tt_rcp_no == sr_tt_rcp_no)

    query = await db.execute(stmt_voc)
    query_result = query.first()
    query_keys = query.keys()

    if not query_result:
        return schemas.VocSpecOutput(
            voc_user_info='',
            bts_summary=[]
        )

    voc_user_info = schemas.VocUserInfo(**dict(zip(query_keys, query_result)))

    # 2 bts summary list ( by voc.base_date + voc.svc_cont_id )
    #s1ap 발생, 실패
    sum_s1ap_cnt = func.sum(func.ifnull(models.VocSpec.s1ap_cnt, 0)).label("s1ap_cnt")
    sum_s1ap_fail_cnt = func.sum(func.ifnull(models.VocSpec.s1ap_fail_cnt, 0)).label("s1ap_fail_cnt")

    #rsrp 평균, 불량 , rsrq 불량
    sum_rsrp_cnt = func.sum(func.ifnull(models.VocSpec.rsrp_cnt,0)).label("rsrp_cnt")
    sum_rsrp_sum = func.sum(func.ifnull(models.VocSpec.rsrp_sum,0)).label("rsrp_sum")
    sum_rsrp_m105d_cnt = func.sum(func.ifnull(models.VocSpec.rsrp_m105d_cnt,0)).label("rsrp_m105d_cnt")
    sum_rsrp_m110d_cnt = func.sum(func.ifnull(models.VocSpec.rsrp_m110d_cnt,0)).label("rsrp_m110d_cnt")
    sum_rsrp_bad_cnt = func.sum(
                                func.ifnull(models.VocSpec.rsrp_m105d_cnt, 0)
                                + func.ifnull(models.VocSpec.rsrp_m110d_cnt, 0)
                        ).label("rsrp_bad_cnt")


    sum_rsrq_m15d_cnt = func.sum(func.ifnull(models.VocSpec.rsrq_m15d_cnt,0)).label("rsrq_m15d_cnt")
    sum_rsrq_m17d_cnt = func.sum(func.ifnull(models.VocSpec.rsrq_m17d_cnt,0)).label("rsrq_m17d_cnt")
    sum_rsrq_bad_cnt = func.sum(
                            func.ifnull(models.VocSpec.rsrq_m15d_cnt, 0)
                            + func.ifnull(models.VocSpec.rsrq_m17d_cnt, 0)
                        ).label("rsrq_bad_cnt")
    sum_rsrq_cnt = func.sum(func.ifnull(models.VocSpec.rsrq_cnt,0)).label("rsrq_cnt")
    sum_rsrq_sum = func.sum(func.ifnull(models.VocSpec.rsrq_sum,0)).label("rsrq_sum")

    # rip 평균, 불량
    # sum_rip_bad_cnt = func.sum(func.ifnull(models.VocSpec.new_rip_maxd_cnt, 0)).label("rip_bad_cnt")
    sum_rip_maxd_cnt = func.sum(func.ifnull(models.VocSpec.new_rip_maxd_cnt, 0)).label("rip_maxd_cnt")
    sum_rip_sum = func.sum(func.ifnull(models.VocSpec.rip_sum, 0)).label("rip_sum")
    sum_rip_cnt = func.sum(func.ifnull(models.VocSpec.rip_cnt, 0)).label("rip_cnt")

    # phr 평균, 불량
    sum_phr_m3d_cnt = func.sum(func.ifnull(models.VocSpec.new_phr_m3d_cnt, 0)).label("phr_m3d_cnt")
    sum_phr_mind_cnt = func.sum(func.ifnull(models.VocSpec.new_phr_mind_cnt, 0)).label("phr_mind_cnt")
    sum_phr_sum = func.sum(func.ifnull(models.VocSpec.phr_sum,0)).label("phr_sum")
    sum_phr_cnt = func.sum(func.ifnull(models.VocSpec.phr_cnt,0)).label("phr_cnt")
    sum_phr_bad_cnt = func.sum(
                            func.ifnull(models.VocSpec.new_phr_m3d_cnt, 0)
                            + func.ifnull(models.VocSpec.new_phr_mind_cnt, 0)
                        ).label("phr_bad_cnt")


    sum_nr_rsrp_cnt = func.sum(func.ifnull(models.VocSpec.nr_rsrp_cnt, 0)).label("nr_rsrp_cnt")
    sum_nr_rsrp_sum = func.sum(func.ifnull(models.VocSpec.nr_rsrp_sum, 0)).label("nr_rsrp_sum")


    # 자망절단, 총절단
    sum_volte_try_cacnt = func.sum(func.ifnull(models.VocSpec.volte_try_cacnt, 0)).label("volte_try_cacnt")
    sum_volte_comp_cacnt = func.sum(func.ifnull(models.VocSpec.volte_comp_cacnt, 0)).label("volte_comp_cacnt")
    sum_volte_self_fail_cacnt = func.sum(func.ifnull(models.VocSpec.volte_self_fail_cacnt,0)).label("volte_self_fail_cacnt")
    sum_volte_other_fail_cacnt = func.sum(func.ifnull(models.VocSpec.volte_other_fail_cacnt,0)).label("volte_other_fail_cacnt")
    sum_volte_fail_cacnt = func.sum(func.ifnull(models.VocSpec.volte_self_fail_cacnt,0) +
                                    func.ifnull(models.VocSpec.volte_other_fail_cacnt,0)).label("volte_fail_cacnt")

    entities_bts = [
        models.VocSpec.base_date,  # label("기준년원일"),
        models.VocSpec.svc_cont_id,
        models.VocSpec.equip_cd,
        models.VocSpec.equip_nm,
        models.VocSpec.latit_val,
        models.VocSpec.lngit_val,
        models.VocSpec.cell_cd,

    ]
    entities_bts_groupby = [
        sum_s1ap_cnt,           # s1ap발생
        sum_s1ap_fail_cnt,      # s1ap실패
        sum_rsrp_m105d_cnt,  # rsrp불량(-109~-105)
        sum_rsrp_m110d_cnt,  # rsrp불량(min~-110)
        sum_rsrp_bad_cnt,       # rsrp불량
        sum_rsrp_cnt,           # rsrp
        sum_rsrp_sum,           # rsrp
        sum_rsrq_m15d_cnt,       # rsrq불량( -16.5~-15)
        sum_rsrq_m17d_cnt,       # rsrq불량(min~-17)
        sum_rsrq_bad_cnt,       # rsrq불량
        sum_rsrq_sum,            # rsrq 합
        sum_rsrq_cnt,            # rsrq 건수
        sum_rip_maxd_cnt,        # rip 불량(-091.9~max)
        sum_rip_sum,            # rip 합
        sum_rip_cnt,            # rip 건수
        sum_phr_m3d_cnt,        # phr m3d (-3~0.9)
        sum_phr_mind_cnt,       # phr mind (min~-3.1 )
        sum_phr_bad_cnt,        # phr 불량
        sum_phr_sum,            # phr
        sum_phr_cnt,            # phr
        sum_nr_rsrp_cnt,
        sum_nr_rsrp_sum,
        sum_volte_try_cacnt,
        sum_volte_comp_cacnt,
        sum_volte_self_fail_cacnt,  # 자망절단
        sum_volte_other_fail_cacnt,  # 타망절단
        sum_volte_fail_cacnt,  # 총절단
    ]

    stmt_bts = select(*entities_bts, *entities_bts_groupby)
    ref_day = (datetime.strptime(voc_user_info.base_date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    stmt_bts = stmt_bts.where(between(models.VocSpec.base_date, ref_day, voc_user_info.base_date))
    stmt_bts = stmt_bts.where(models.VocSpec.svc_cont_id == voc_user_info.svc_cont_id)
    stmt_bts = stmt_bts.group_by(*entities_bts).order_by(sum_volte_self_fail_cacnt.desc())
    query = await db.execute(stmt_bts)

    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    bts_summary_list = list(map(lambda x: schemas.BtsSummary(**dict(zip(query_keys, x))), query_result))

    return schemas.VocSpecOutput(
        voc_user_info=voc_user_info,
        bts_summary=bts_summary_list
    )


async def get_voc_trend_item_by_group_date(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                           start_date: str = None, end_date: str = None):
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    voc_cnt = func.count(models.VocList.sr_tt_rcp_no_cnt).label("voc_cnt")

    # 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.VocList.base_date, start_date, end_date))

    # 상품 조건
    if prod and prod != "전체":
        stmt_where_and.append(models.VocList.anals_3_prod_level_nm == prod)

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_sel_nm = models.VocList.mkng_cmpn_nm
    elif code == "본부별":
        code_tbl_nm = select(models.OrgCode.bonbu_nm, models.OrgCode.oper_team_nm).\
                    group_by(models.OrgCode.bonbu_nm, models.OrgCode.oper_team_nm).subquery()
        code_sel_nm = code_tbl_nm.c.oper_team_nm
        code_where_nm = code_tbl_nm.c.bonbu_nm

        stmt_sel_nm = models.VocList.oper_team_nm
    elif code == "센터별":
        # code_tbl_nm = models.OrgCode
        # code_sel_nm = models.OrgCode.area_jo_nm
        # code_where_nm = models.OrgCode.biz_hq_nm

        stmt_sel_nm = models.VocList.biz_hq_nm
    elif code == "팀별":
        # stmt_sel_nm = models.VolteFail.oper_team_nm
        # 22.11.22
        # 지하철엔지니어링부->oper_team_nm사용,그외->area_team_nm&&not지하철
        if "지하철엔지니어링부" in where_ins:
            stmt_sel_nm = models.VocList.oper_team_nm
        else:
            code_tbl_nm = select(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm).\
                    group_by(models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm).subquery()
            code_sel_nm = code_tbl_nm.c.area_jo_nm
            code_where_nm = code_tbl_nm.c.oper_team_nm

            stmt_sel_nm = models.VocList.area_jo_nm
            stmt_where_and.append(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "조별":
        stmt_sel_nm = models.VocList.area_jo_nm
        stmt_where_and.append(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.sido_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.sido_nm

        stmt_sel_nm = models.VocList.eup_myun_dong_nm
    elif code == "시군구별":
        code_tbl_nm = select(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm). \
            group_by(models.AddrCode.eup_myun_dong_nm, models.AddrCode.gun_gu_nm).subquery()
        code_sel_nm = code_tbl_nm.c.eup_myun_dong_nm
        code_where_nm = code_tbl_nm.c.gun_gu_nm

        stmt_sel_nm = models.VocList.eup_myun_dong_nm
    elif code == "읍면동별":
        stmt_sel_nm = models.VocList.eup_myun_dong_nm
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if code_tbl_nm == None:  # code table 미사용시
        stmt_where_and.append(stmt_sel_nm.in_(where_ins))

        stmt = select(
            stmt_sel_nm.label("code"),
            models.VocList.base_date.label("date"),
            voc_cnt
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.VocList.base_date, stmt_sel_nm)
    else:  # code table 사용시
        stmt_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        stmt_where_and.append(stmt_sel_nm.in_(stmt_wh))

        st_in = select(
            models.VocList.base_date,
            stmt_sel_nm.label("code"),
            voc_cnt,
        ).where(
            and_(*stmt_where_and)
        ).group_by(models.VocList.base_date, stmt_sel_nm)

        stmt = select(
            code_where_nm.label("code"),
            st_in.c.base_date.label("date"),
            func.sum(st_in.c.voc_cnt).label("value"),
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in.c.code
        ).group_by(
            st_in.c.base_date,
            code_where_nm
        )
    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result = query_cut.all()
    query_keys = query_cut.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.VocTrendOutput(date=r[1], value=r[2]) for r in query_result if r[0] == code]
        list_items.append(schemas.VocTrendItemOutput(title=code, data=t_l))

    return list_items


# 조기준X
async def get_voc_trend_by_group_month(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                 start_month: str = None, end_month: str = None):
    # 1000가입자당  VOC건수
    voc_cnt = func.count(func.ifnull(models.VocListMM.sr_tt_rcp_no, 0)).label("voc_cnt")
    sbscr_cnt = func.sum(func.ifnull(models.SubscrMM.bprod_maint_sbscr_cascnt, 0)).label("sbscr_cnt")

    stmt_sbscr = select(models.SubscrMM.base_ym, sbscr_cnt)
    stmt_voc = select(models.VocListMM.base_ym, voc_cnt)

    # 기간
    if not end_month:
        end_month = start_month

    if start_month:
        stmt_sbscr = stmt_sbscr.where(between(models.SubscrMM.base_ym, start_month, end_month))
        stmt_voc = stmt_voc.where(between(models.VocListMM.base_ym, start_month, end_month))

    txt_l = []
    if group != "":
        txt_l = group.split("|")

    # 선택 조건(센터,팀,시,군구)
    if code == "본부별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.new_hq_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
        # stmt_sbscr = stmt_sbscr.where(models.Subscr.oper_team_nm.in_(stmt_where))
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.biz_hq_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.oper_team_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_where = select(models.AddrCode.gun_gu_nm).where(models.AddrCode.sido_nm.in_(txt_l))
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.gun_gu_nm.in_(stmt_where))
        stmt_voc = stmt_voc.where(models.VocListMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.gun_gu_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.gun_gu_nm.in_(txt_l))
    else:
        pass

    # 상품 조건
    if prod and prod != "전체":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.anals_3_prod_level_nm == prod)
        stmt_voc = stmt_voc.where(models.VocListMM.anals_3_prod_level_nm == prod)

    stmt_sbscr = stmt_sbscr.group_by(models.SubscrMM.base_ym).having(sbscr_cnt > 0).\
        order_by(models.SubscrMM.base_ym.asc()).subquery()
    stmt_voc = stmt_voc.group_by(models.VocListMM.base_ym).order_by(models.VocListMM.base_ym.asc()).subquery()

    stmt = select(
            stmt_sbscr.c.base_ym.label("date"),
            func.ifnull(func.round(stmt_voc.c.voc_cnt / stmt_sbscr.c.sbscr_cnt * 1000.0, 4), 0.0).label("value"),
            func.ifnull(stmt_voc.c.voc_cnt, 0).label("voc_cnt"),
            func.ifnull(stmt_sbscr.c.sbscr_cnt, 0).label("sbscr_cnt"),
            ).outerjoin(
                stmt_voc,
                (stmt_voc.c.base_ym == stmt_sbscr.c.base_ym)
            )

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendMonthOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend


# 조기준X
async def get_voc_trend_item_by_group_month(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                           start_month: str = None, end_month: str = None):
    code_tbl_nm = None
    code_sel_nm = Column()  # code테이블 select()
    code_where_nm = Column()  # code테이블 where()

    where_ins = []  # code테이블, voc 테이블 where in (a, b, c)
    sbscr_where_and = [] # sbscr table where list
    voc_where_and = []  # voc table where list

    voc_cnt = func.count(models.VocListMM.sr_tt_rcp_no).label("voc_cnt")
    sbscr_cnt = func.sum(models.SubscrMM.bprod_maint_sbscr_cascnt).label("sbscr_cnt")

    # 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    sbscr_where_and.append(between(models.SubscrMM.base_ym, start_month, end_month))
    voc_where_and.append(between(models.VocListMM.base_ym, start_month, end_month))

    # 상품 조건
    if prod and prod != "전체":
        sbscr_where_and.append(models.SubscrMM.anals_3_prod_level_nm == prod)
        voc_where_and.append(models.VocListMM.anals_3_prod_level_nm == prod)


    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "본부별":
        sbscr_sel_nm = models.SubscrMM.new_hq_nm
        voc_sel_nm = models.VocListMM.new_hq_nm  # voc 테이블 select 변수
    elif code == "센터별":
        sbscr_sel_nm = models.SubscrMM.biz_hq_nm
        voc_sel_nm = models.VocListMM.biz_hq_nm  # voc 테이블 select 변수
    elif code == "팀별":
        sbscr_sel_nm = models.SubscrMM.oper_team_nm
        voc_sel_nm = models.VocListMM.oper_team_nm  # voc 테이블 select 변수

    elif code == "시도별":
        sbscr_sel_nm = models.SubscrMM.sido_nm
        voc_sel_nm = models.VocListMM.sido_nm  # voc 테이블 select 변수
    elif code == "시군구별":
        sbscr_sel_nm = models.SubscrMM.gun_gu_nm
        voc_sel_nm = models.VocListMM.gun_gu_nm  # voc 테이블 select 변수
    else:
        raise ex.SqlFailureEx

    # stmt 생성

    sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))

    st_sbscr = select(
        sbscr_sel_nm.label("code"),
        models.SubscrMM.base_ym,
        sbscr_cnt
    ).where(
        and_(*sbscr_where_and)
    ).group_by(models.SubscrMM.base_ym, sbscr_sel_nm)

    voc_where_and.append(voc_sel_nm.in_(where_ins))
    st_voc = select(
        models.VocListMM.base_ym,
        voc_sel_nm.label("code"),
        voc_cnt
    ).where(
        and_(*voc_where_and)
    ).group_by(
        models.VocListMM.base_ym,
        voc_sel_nm
    ).subquery()

    stmt = select(
        st_sbscr.c.code,
        st_sbscr.c.base_ym.label("date"),
        func.ifnull(func.round(st_voc.c.voc_cnt / st_sbscr.c.sbscr_cnt * 1000.0, 4), 0.0).label("value"),
        st_sbscr.c.sbscr_cnt,
        st_voc.c.voc_cnt,
    ).outerjoin(
        st_voc,
        and_(st_sbscr.c.base_ym == st_voc.c.base_ym, st_sbscr.c.code == st_voc.c.code)
    )
    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result = query_cut.all()
    query_keys = query_cut.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.VocTrendMonthOutput(**r) for r in query_result if r[0] == code]
        list_items.append(schemas.VocTrendItemMonthOutput(title=code, data=t_l))

    return list_items



