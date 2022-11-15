from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from app import schemas
from sqlalchemy import func, select, between, case, and_, Column
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

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm == prod)

    # 선택 조건
    if code == "제조사별":
        code_val = models.VocList.mkng_cmpn_nm
    elif code == "센터별":
        code_val = models.VocList.biz_hq_nm
    elif code == "팀별":
        code_val = models.VocList.oper_team_nm
    elif code == "조별":
        code_val = models.VocList.area_jo_nm
    elif code == "시도별":
        code_val = models.VocList.sido_nm
    elif code == "시군구별":
        code_val = models.VocList.gun_gu_nm
    elif code == "읍면동별":
        code_val = models.VocList.eup_myun_dong_nm
    else:
        code_val = None
    
    # code의 값목록 : 삼성|노키아
    if (code_val) and (group):
        txt_l = group.split("|")
        stmt = stmt.where(code_val.in_(txt_l))

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

    # 상품 조건
    if prod and prod != "전체":
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm == prod)

    # 선택 조건
    if code == "제조사별":
        code_val = models.VocList.mkng_cmpn_nm
    elif code == "센터별":
        code_val = models.VocList.biz_hq_nm
    elif code == "팀별":
        code_val = models.VocList.oper_team_nm
    elif code == "조별":
        code_val = models.VocList.area_jo_nm
    elif code == "시도별":
        code_val = models.VocList.sido_nm
    elif code == "시군구별":
        code_val = models.VocList.gun_gu_nm
    elif code == "읍면동별":
        code_val = models.VocList.eup_myun_dong_nm
    else:
        code_val = None

    # code의 값목록 : 삼성|노키아
    if code_val != "" and group !="":
        txt_l = group.split("|")
        stmt = stmt.where(code_val.in_(txt_l))

    # stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).subquery()
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).limit(limit)

    # stmt_rk = select([
    #     func.rank().over(order_by=stmt.c.voc_cnt.desc()).label("RANK"),
    #     *stmt.c
    # ])

    # query = db.execute(stmt_rk)
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
    elif code == "센터별":
        stmt_voc = stmt_voc.where(models.VocList.biz_hq_nm.in_(txt_l))
    elif code == "팀별":
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_voc = stmt_voc.where(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_voc = stmt_voc.where(models.VocList.gun_gu_nm.in_(txt_l))
    else:
        pass

    # 상품 조건
    if prod and prod != "전체":
        stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm == prod)

    stmt_voc = stmt_voc.group_by(models.VocList.base_date).order_by(models.VocList.base_date.asc())



    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend


# async def get_voc_trend_by_group_date2(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
#                                  start_date: str = None, end_date: str = None):
#     # 1000가입자당  VOC건수
#     voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no_cnt, 0)).label("voc_cnt")
#     sbscr_cnt = func.sum(func.ifnull(models.Subscr.bprod_maint_sbscr_cascnt, 0)).label("sbscr_cnt")
#
#     stmt_sbscr = select(models.Subscr.base_date, sbscr_cnt)
#     stmt_voc = select(models.VocList.base_date, voc_cnt)
#
#     # 기간
#     if not end_date:
#         end_date = start_date
#
#     if start_date:
#         stmt_sbscr = stmt_sbscr.where(between(models.Subscr.base_date, start_date, end_date))
#         stmt_voc = stmt_voc.where(between(models.VocList.base_date, start_date, end_date))
#
#     txt_l = []
#     if group != "":
#         txt_l = group.split("|")
#
#     # 선택 조건
#     if code == "제조사별":
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.mkng_cmpn_nm.in_(txt_l))
#         stmt_voc = stmt_voc.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
#     elif code == "센터별":
#         # stmt_where = select(models.OrgCode.oper_team_nm).where(models.OrgCode.biz_hq_nm.in_(txt_l))
#         # stmt_sbscr = stmt_sbscr.where(models.Subscr.oper_team_nm.in_(stmt_where))
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.biz_hq_nm.in_(txt_l))
#         stmt_voc = stmt_voc.where(models.VocList.biz_hq_nm.in_(txt_l))
#     elif code == "팀별":
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.oper_team_nm.in_(txt_l))
#         stmt_voc = stmt_voc.where(models.VocList.oper_team_nm.in_(txt_l))
#     elif code == "시도별":
#         stmt_where = select(models.AddrCode.gun_gu_nm).where(models.AddrCode.sido_nm.in_(txt_l))
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.gun_gu_nm.in_(stmt_where))
#         stmt_voc = stmt_voc.where(models.VocList.sido_nm.in_(txt_l))
#     elif code == "시군구별":
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.gun_gu_nm.in_(txt_l))
#         stmt_voc = stmt_voc.where(models.VocList.gun_gu_nm.in_(txt_l))
#     else:
#         pass
#
#     # 상품 조건
#     if prod and prod != "전체":
#         stmt_sbscr = stmt_sbscr.where(models.Subscr.anals_3_prod_level_nm == prod)
#         stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm == prod)
#
#     stmt_sbscr = stmt_sbscr.group_by(models.Subscr.base_date).having(sbscr_cnt > 0).\
#         order_by(models.Subscr.base_date.asc()).subquery()
#     stmt_voc = stmt_voc.group_by(models.VocList.base_date).order_by(models.VocList.base_date.asc()).subquery()
#
#     stmt = select(
#             stmt_sbscr.c.base_date.label("date"),
#             func.ifnull(func.round(stmt_voc.c.voc_cnt / stmt_sbscr.c.sbscr_cnt * 1000.0, 4), 0.0).label("value"),
#             ).outerjoin(
#                 stmt_voc,
#                 (stmt_voc.c.base_date == stmt_sbscr.c.base_date)
#             )
#
#     # print(stmt.compile(compile_kwargs={"literal_binds": True}))
#     query = await db.execute(stmt)
#     query_result = query.all()
#     query_keys = query.keys()
#
#     list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
#     return list_voc_trend


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
    # 자망절단, 총절단
    sum_volte_self_fail_cacnt = func.sum(func.ifnull(models.VocSpec.volte_self_fail_cacnt,0)).label("volte_self_fail_cacnt")
    sum_volte_fail_cacnt = func.sum(func.ifnull(models.VocSpec.volte_self_fail_cacnt,0) +
                                    func.ifnull(models.VocSpec.volte_other_fail_cacnt,0)).label("volte_fail_cacnt")
    # SRU발생건, nSINR평균 불량
    #rsrp 평균, 불량 , rsrq 불량
    sum_rsrp_cnt = func.sum(func.ifnull(models.VocSpec.rsrp_cnt,0)).label("rsrp_cnt")
    sum_rsrp_sum = func.sum(func.ifnull(models.VocSpec.rsrp_sum,0)).label("rsrp_sum")
    sum_rsrp_bad_cnt = func.sum(
                                func.ifnull(models.VocSpec.rsrp_m105d_cnt, 0)
                                + func.ifnull(models.VocSpec.rsrp_m110d_cnt, 0)
                        ).label("rsrp_bad_cnt")
    sum_rsrq_bad_cnt = func.sum(
                            func.ifnull(models.VocSpec.rsrq_m15d_cnt, 0)
                            + func.ifnull(models.VocSpec.rsrq_m17d_cnt, 0)
                        ).label("rsrq_bad_cnt")
    # rip 평균, 불량
    sum_rip_sum = func.sum(func.ifnull(models.VocSpec.rip_sum,0)).label("rip_sum")
    sum_rip_bad_cnt = func.sum(func.ifnull(models.VocSpec.new_rip_maxd_cnt, 0)).label("rip_bad_cnt")
    sum_rip_cnt = func.sum(func.ifnull(models.VocSpec.rip_cnt, 0)).label("rip_cnt")
    # phr 평균, 불량
    sum_phr_sum = func.sum(func.ifnull(models.VocSpec.phr_sum,0)).label("phr_sum")
    sum_phr_cnt = func.sum(func.ifnull(models.VocSpec.phr_cnt,0)).label("phr_cnt")
    sum_phr_bad_cnt = func.sum(
                            func.ifnull(models.VocSpec.new_phr_m3d_cnt, 0)
                            + func.ifnull(models.VocSpec.new_phr_mind_cnt, 0)
                        ).label("phr_bad_cnt")
    # sum_new_phr_m3d_cnt = func.sum(func.ifnull(models.VocSpec.new_phr_m3d_cnt, 0)).label("new_phr_m3d_cnt")
    # sum_new_phr_mind_cnt = func.sum(func.ifnull(models.VocSpec.new_phr_mind_cnt, 0)).label("new_phr_mind_cnt")
    # sum_phr_cnt = func.sum(func.ifnull(models.VocSpec.phr_cnt, 0)).label("phr_cnt")
    sum_nr_rsrp_cnt = func.sum(func.ifnull(models.VocSpec.nr_rsrp_cnt, 0)).label("nr_rsrp_cnt")

    entities_bts = [
        # models.VocSpec.base_date,  # label("기준년원일"),
        models.VocSpec.svc_cont_id,
        models.VocSpec.equip_cd,
        models.VocSpec.equip_nm,
        models.VocSpec.latit_val,
        models.VocSpec.lngit_val,
    ]
    entities_bts_groupby = [
        sum_s1ap_cnt,           # s1ap발생
        sum_s1ap_fail_cnt,      # s1ap실패
        sum_volte_self_fail_cacnt, # 자망절단
        sum_volte_fail_cacnt,   # 총절단
        sum_rsrp_cnt,           # rsrp
        sum_rsrp_sum,           # rsrp
        sum_rsrp_bad_cnt,       # rsrp불량
        sum_rsrq_bad_cnt,       # rsrq불량
        sum_rip_sum,            # rip
        sum_rip_cnt,            # rip
        sum_rip_bad_cnt,        # rip 불량
        sum_rip_cnt,            # rip건수
        sum_phr_sum,            # phr
        sum_phr_cnt,            # phr
        sum_phr_bad_cnt,        # phr 불량
        sum_nr_rsrp_cnt,
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

    # sbscr_sel_nm = Column()  # sbscr select()
    # voc_sel_nm = Column()  # volc select()

    where_ins = []  # code테이블, voc테이블 where in (a, b, c)
    sbscr_where_and = []  # sbscr 테이블 where list
    voc_where_and = []  # voc 테이블 where list

    voc_cnt = func.count(models.VocList.sr_tt_rcp_no_cnt).label("voc_cnt")
    sbscr_cnt = func.sum(models.Subscr.bprod_maint_sbscr_cascnt).label("sbscr_cnt")

    # 기간
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    sbscr_where_and.append(between(models.Subscr.base_date, start_date, end_date))
    voc_where_and.append(between(models.VocList.base_date, start_date, end_date))

    # 상품 조건
    if prod and prod != "전체":
        sbscr_where_and.append(models.Subscr.anals_3_prod_level_nm == prod)
        voc_where_and.append(models.VocList.anals_3_prod_level_nm == prod)

    # code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    # 선택 조건
    if code == "제조사별":
        sbscr_sel_nm = models.Subscr.mkng_cmpn_nm
        voc_sel_nm = models.VocList.mkng_cmpn_nm  # voc 테이블 select 변수

    elif code == "센터별":
        # code_tbl_nm = models.OrgCode
        # code_sel_nm = models.OrgCode.oper_team_nm
        # code_where_nm = models.OrgCode.biz_hq_nm

        sbscr_sel_nm = models.Subscr.biz_hq_nm
        voc_sel_nm = models.VocList.biz_hq_nm  # voc 테이블 select 변수
    elif code == "팀별":
        sbscr_sel_nm = models.Subscr.oper_team_nm
        voc_sel_nm = models.VocList.oper_team_nm  # voc 테이블 select 변수
    elif code == "시도별":
        code_tbl_nm = models.AddrCode
        code_sel_nm = models.AddrCode.gun_gu_nm
        code_where_nm = models.AddrCode.sido_nm

        sbscr_sel_nm = models.Subscr.gun_gu_nm
        voc_sel_nm = models.VocList.sido_nm  # voc 테이블 select 변수
    elif code == "시군구별":
        sbscr_sel_nm = models.Subscr.gun_gu_nm
        voc_sel_nm = models.VocList.gun_gu_nm  # voc 테이블 select 변수
    else:
        raise ex.SqlFailureEx

    # stmt 생성
    if not code_tbl_nm:  # code table 미사용시
        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))

        st_sbscr = select(
            sbscr_sel_nm.label("code"),
            models.Subscr.base_date,
            sbscr_cnt
        ).where(
            and_(*sbscr_where_and)
        ).group_by(models.Subscr.base_date, sbscr_sel_nm)

    else:  # code table 사용시
        st_sbscr_wh = select(code_sel_nm).distinct().where(code_where_nm.in_(where_ins))
        sbscr_where_and.append(sbscr_sel_nm.in_(st_sbscr_wh))

        st_in_sbscr = select(
            sbscr_sel_nm.label("code"),
            models.Subscr.base_date,
            sbscr_cnt
        ).where(
            and_(*sbscr_where_and)
        ).group_by(models.Subscr.base_date, sbscr_sel_nm)

        st_sbscr = select(
            code_where_nm.label("code"),
            st_in_sbscr.c.base_date,
            func.sum(st_in_sbscr.c.sbscr_cnt).label("sbscr_cnt")
        ).outerjoin(
            code_tbl_nm,
            code_sel_nm == st_in_sbscr.c.code
        ).group_by(
            st_in_sbscr.c.base_date,
            code_where_nm
        )

    voc_where_and.append(voc_sel_nm.in_(where_ins))
    st_voc = select(
        models.VocList.base_date,
        voc_sel_nm.label("code"),
        voc_cnt
    ).where(
        and_(*voc_where_and)
    ).group_by(
        models.VocList.base_date,
        voc_sel_nm
    ).subquery()

    stmt = select(
        st_sbscr.c.code,
        st_sbscr.c.base_date,
        # st_sbscr.c.sbscr_cnt,
        # st_voc.c.voc_cnt,
        func.ifnull(func.round(st_voc.c.voc_cnt / st_sbscr.c.sbscr_cnt * 1000.0, 4), 0.0).label("value")
    ).outerjoin(
        st_voc,
        and_(st_sbscr.c.base_date == st_voc.c.base_date, st_sbscr.c.code == st_voc.c.code)
    )

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.all()
    # query_keys = query.keys()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.VocTrendOutput(date=r[1], value=r[2]) for r in query_result if r[0] == code]
        list_items.append(schemas.VocTrendItemOutput(title=code, data=t_l))

    return list_items


