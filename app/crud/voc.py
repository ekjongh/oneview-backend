########################################################################################################################
# VOC 서비스 모듈
#
# [ 서비스 목록 ]
# * 기지국별 VOC Worst TOP 10 : get_worst10_bts_by_group_date
# * 단말별 품질 VOC Worst TOP10 : get_worst10_hndset_by_group_date
# * 일자별 VOC 리스트 : get_voc_list_by_group_date
#   - VOC 상세분석 페이지 > 상단 VOC 목록
# * 전일데이터까지 VOC 트랜드 : get_voc_trend_by_group_date (Fade-out 예정) 주1)
# * (KPI용) VOC 요약(이력 or 실시간) : get_voc_summary_by_group_date
#     ├- 이력 : get_voc_summary_by_group_past : SUM_VOC_TXN
#     └- 실시간 : get_voc_summary_by_group_today : SUM_VOC_TEST
#   - VOCAI 당일누적 전국 실시간 VOC 비중
#   - 3월 프론트 개발예정이고 데이터 들어오면 로직검증 필요
#   - 대상 테이블명 : SUM_VOC_TXN, SUM_VOC_TEST(임시 -> 확정시 변경예정)
# * VOC 상세 : get_voc_spec_by_srno
#   - VOC 상세분석 페이지 > 하단 오른쪽 VOC 발생고객 사용기지국 품질요약
# * 일자별 VOC 트랜드 : get_voc_trend_item_by_group_date
#   - 주1) 없애고, 위의 함수로 통합예정
#   - 대상 테이블: SUM_VOC_TXN
# * 월별 VOC 트랜드 : get_voc_trend_by_group_month 주2)
#   - 대상 테이블: SUM_VOC_TXN_MM, 건수+1000회선당 건수 그래서 가입자 테이블 사용: SUM_SBSTR_CNT
# * 월별 VOC 트랜드 : get_voc_trend_item_by_group_month
#   - 주2) 서비스 유사 + 그룹핑 항목 추가 가능(조직별,제조사, 상품,...)
# * XXXXXX : get_voc_trend_by_group_hour_stack
# * XXXXXX : get_voc_count_item_by_group_hour
#
# [ 관련 테이블 리스트 ]
# * SUM_VOC_DTL_TXN : VOC 상세 분석 / VOC 고객품질(사용자기지국품질요약, 상세품질조회)
# * SUM_VOC_TEST :
# * SUM_VOC_TXN : VOC 일별추이 WORST(기지국, 단말)
# * SUM_VOC_TXN_MM : VOC 월별추이(단말별 가입자수 월합계)
# * SUM_VOC_TXN_RT_TMP :
#
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.29 - 주석추가 (작업중)
# 2023.03.02 - 김아영 차장님께 모듈 설명 듣고 1차 주석 추가
#
########################################################################################################################
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.errors import exceptions as ex
from app import schemas
from sqlalchemy import func, select, between, case, and_, or_, Column, distinct, literal
from datetime import datetime, timedelta

from app import models
from app.utils.query_utils import band_to_equipcd2


async def get_worst10_bts_by_group_date(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                   band:str=None, start_date: str = None, end_date: str = None, limit: int = 10):
    """ 기지국별 VOC Worst Top 10을 제공하는 함수
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - band : 1.8, 3.5
        - start_date :  조회기간(시작일자, 예: 20230201)
        - end_date :  조회기간(종료일자, 예: 20230229)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
        - SUM_VOC_TXN
    """
    # 기지국별 VOC Worst TOP 10
    voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no_cnt, 0))
    voc_cnt = func.coalesce(voc_cnt, 0).label("voc_cnt")
    juso = func.concat(models.VocList.gun_gu_nm+' ', models.VocList.eup_myun_dong_nm).label("juso")


    # entities - 쿼리문 SELECT에 나열되는 컬럼들
    # entities_groupby - 집계항목
    #
    entities = [
        models.VocList.equip_cd,
        models.VocList.equip_nm,
        # juso,
        # models.VocList.biz_hq_nm.label("center"),
        # models.VocList.oper_team_nm.label("team"),
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
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm.in_(prod_l))

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt = stmt.where(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.VocList.oper_team_nm.in_(txt_l))
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
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 주파수대역 조건
    if band :
        equipcd2 = band_to_equipcd2(band)
        stmt = stmt.where(func.substring(models.VocList.equip_cd,1,2).in_(equipcd2))


    stmt = stmt.where(models.VocList.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).limit(limit)
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    print(stmt)

    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_voc_bts = list(map(lambda x: schemas.VocBtsOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_bts


async def get_worst10_hndset_by_group_date(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                      start_date: str = None, end_date: str = None, limit: int = 10):
    """ 단말별 품질 VOC Worst TOP10
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - band : 1.8, 3.5
        - start_date :  조회기간(시작일자, 예: 20230201)
        - end_date :  조회기간(종료일자, 예: 20230229)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
        - SUM_VOC_TXN
    """
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
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt = stmt.where(models.VocList.anals_3_prod_level_nm.in_(prod_l))

    # 선택 조건
    if code == "제조사별":
        stmt = stmt.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt = stmt.where(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt = stmt.where(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt = stmt.where(models.VocList.oper_team_nm.in_(txt_l))
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
    elif code =="전국" or code =="전체" or code =="all":
        pass
    else:
        code_val = None
        raise ex.NotFoundAccessKeyEx

    stmt = stmt.where(models.VocList.area_jo_nm!="값없음")
    stmt = stmt.group_by(*entities).order_by(voc_cnt.desc()).limit(limit)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_worst_voc_hndset = list(map(lambda x: schemas.VocHndsetOutput(**dict(zip(query_keys, x))), query_result))
    return list_worst_voc_hndset


async def get_voc_list_by_group_date(db: AsyncSession, group: str, start_date: str = None, end_date: str = None,
                               limit: int = 1000):
    """ 일자별 VOC 리스트를 제공하는 함수
        [ 파라미터 ]
        - start_date : 조회시작일자(예: 20230303)
        - end_date : 조회종료일자(예: 20230303)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
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
        models.VocList.equip_cd,        # label("주기지국"),
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


async def get_voc_trend_by_group_date(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                 start_date: str = None, end_date: str = None):
    """ 전일데이터까지 VOC 트랜드 - 폐기 예정 (일자별 VOC 트랜드로 통합)
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
        - end_date :  조회기간(종료일자, 예: 20230229)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    # 전일데이터까지 voc trend

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
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_voc = stmt_voc.where(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_voc = stmt_voc.where(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm.in_(txt_l))
    elif code== "조별":
        stmt_voc = stmt_voc.where(models.VocList.area_jo_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_voc = stmt_voc.where(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_voc = stmt_voc.where(models.VocList.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_voc = stmt_voc.where(models.VocList.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm.in_(prod_l))

    stmt_voc = stmt_voc.group_by(models.VocList.base_date).order_by(models.VocList.base_date.asc())

    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocTrendOutput(**dict(zip(query_keys, x))), query_result))
    return list_voc_trend


async def get_voc_summary_by_group_date(db: AsyncSession, code: str = None, group: str = None,
                                 start_date: str = None):
    """ (KPI용) VOC 요약(이력 or 실시간)을 제공하는 함수
        * 조회시작일자가 당일인 경우 => 실시간 (함수: get_voc_summary_by_group_today, 테이블: SUM_VOC_TEST)
        * 조회시작일자가 당일이 아닌 경우 => 이력 (함수: get_voc_summary_by_group_past, 테이블: SUM_VOC_TXN
        [ 파라미터 ]
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    today = datetime.today().strftime("%Y%m%d")
    if start_date==today:
        return await get_voc_summary_by_group_today(db, code, group, start_date)
    else:
        return await get_voc_summary_by_group_past(db, code, group, start_date)


async def get_voc_summary_by_group_past(db: AsyncSession, code: str = None, group: str = None,
                                 start_date: str = None):
    """" (KPI용) VOC 요약(이력)을 제공하는 함수
        [ 파라미터 ]
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
         [ 반환값 ]
         [ 관련 테이블 ]
    """
    stmt_where_and = []
    ## voc cnt, last time,
    g5_voc_cnt = func.sum(case([(models.VocList.anals_3_prod_level_nm == '5G', 1)], else_=0)).label("g5_voc")
    lte_voc_cnt = func.sum(case([(models.VocList.anals_3_prod_level_nm == 'LTE', 1)], else_=0)).label("lte_voc")
    max_rcp_no = func.max(models.VocList.sr_tt_rcp_no)
    last_time = func.concat(func.substring(max_rcp_no, 11, 2), ":", func.substring(max_rcp_no, 13, 2)).label(
        "last_time")

    stmt_voc = select(models.VocList.base_date.label("date"),last_time, g5_voc_cnt, lte_voc_cnt)

    # 기간
    if start_date:
        stmt_voc = stmt_voc.where(models.VocList.base_date == start_date)

    txt_l = []
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.VocList.mkng_cmpn_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_where_and.append(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_where_and.append(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_where_and.append(models.VocList.oper_team_nm.in_(txt_l))
    elif code== "조별":
        stmt_where_and.append(models.VocList.area_jo_nm.in_(txt_l))
        stmt_where_and.append(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where_and.append(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_where_and.append(models.VocList.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_where_and.append(models.VocList.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    stmt_voc = stmt_voc.where(and_(*stmt_where_and))
    #상품조건
    stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm.in_(["5G","LTE"]))
    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    if not query_result:
        return None
    result = schemas.VocSummaryOutput(**dict(*query_result))

    ## 전국건수 query
    g5_voc_cnt = func.sum(case([(models.VocList.anals_3_prod_level_nm == '5G', 1)], else_=0)).label("g5_all_cnt")
    lte_voc_cnt = func.sum(case([(models.VocList.anals_3_prod_level_nm == 'LTE', 1)], else_=0)).label("lte_all_cnt")
    stmt_voc = select(models.VocList.base_date.label("date"), g5_voc_cnt, lte_voc_cnt)
    # 기간
    if start_date:
        stmt_voc = stmt_voc.where(models.VocList.base_date == start_date)
    # 상품 조건
    stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm.in_(["5G","LTE"]))
    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    result.g5_all_cnt = dict(*query_result)["g5_all_cnt"]
    result.lte_all_cnt = dict(*query_result)["lte_all_cnt"]

    # 비율
    result.g5_all_ratio = round(result.g5_voc/result.g5_all_cnt*100, 2) if result.g5_all_cnt else 0
    result.lte_all_ratio = round(result.lte_voc/result.lte_all_cnt*100, 2) if result.lte_all_cnt else 0

    ## 전주, 전전주
    a_week_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")
    two_weeks_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(14)).strftime("%Y%m%d")
    g5_a_voc_cnt = func.sum(case([( and_(models.VocList.base_date == a_week_ago,
                                      models.VocList.anals_3_prod_level_nm == "5G",
                                      ),1)
                              ], else_=0)).label("g5_a_week_ago")
    g5_two_voc_cnt = func.sum(case([(and_(models.VocList.base_date == two_weeks_ago,
                                          models.VocList.anals_3_prod_level_nm == "5G",
                                          ), 1)
                               ], else_=0)).label("g5_two_weeks_ago")
    lte_a_voc_cnt = func.sum(case([( and_(models.VocList.base_date == a_week_ago,
                                      models.VocList.anals_3_prod_level_nm == "LTE",
                                      ),1)
                              ], else_=0)).label("lte_a_week_ago")
    lte_two_voc_cnt = func.sum(case([(and_(models.VocList.base_date == two_weeks_ago,
                                          models.VocList.anals_3_prod_level_nm == "LTE",
                                          ), 1)
                               ], else_=0)).label("lte_two_weeks_ago")
    stmt_voc = select(g5_a_voc_cnt, g5_two_voc_cnt,lte_a_voc_cnt,lte_two_voc_cnt )

    # 기간 조건
    if start_date:
        stmt_voc = stmt_voc.where(models.VocList.base_date.in_([a_week_ago, two_weeks_ago]))
    # 선택 조건
    stmt_voc = stmt_voc.where(and_(*stmt_where_and))

    # 상품 조건
    stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm.in_(['5G','LTE']))

    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()

    g5_a_week_ago = dict(*query_result)["g5_a_week_ago"]
    g5_two_weeks_ago = dict(*query_result)["g5_two_weeks_ago"]
    lte_a_week_ago = dict(*query_result)["lte_a_week_ago"]
    lte_two_weeks_ago = dict(*query_result)["lte_two_weeks_ago"]

    result.g5_compare_1w = result.g5_voc- g5_a_week_ago if g5_a_week_ago else 0
    result.g5_compare_2w = result.g5_voc - g5_two_weeks_ago if g5_two_weeks_ago else 0
    result.lte_compare_1w = result.lte_voc - lte_a_week_ago if lte_a_week_ago else 0
    result.lte_compare_2w = result.lte_voc - lte_two_weeks_ago if lte_two_weeks_ago else 0

    return result


async def get_voc_summary_by_group_today(db: AsyncSession, code: str = None, group: str = None,
                                 start_date: str = None):
    """" (KPI용) VOC 요약(실시간)을 제공하는 함수
        [ 파라미터 ]
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
         [ 반환값 ]
         [ 관련 테이블 ]
    """
    stmt_where_and = []

    ## 당일누적voc count , 마지막voc time
    g5_voc_cnt = func.sum(case([(models.VocListHH.anals_3_prod_level_nm == '5G', 1)], else_=0)).label("g5_voc")
    lte_voc_cnt = func.sum(case([(models.VocListHH.anals_3_prod_level_nm == 'LTE', 1)], else_=0)).label("lte_voc")
    max_rcp_no = func.max(models.VocListHH.sr_tt_rcp_no)
    last_time = func.concat(func.substring(max_rcp_no, 11, 2), ":", func.substring(max_rcp_no, 13, 2)).label(
        "last_time")

    stmt_voc = select(models.VocListHH.base_date.label("date"),last_time, g5_voc_cnt, lte_voc_cnt)

    # 기간
    if start_date:
        stmt_voc = stmt_voc.where(models.VocListHH.base_date == start_date)

    txt_l = []
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        pass
        # stmt_where_and.append(models.VocListHH.mkng_cmpn_nm.in_(txt_l))
        # stmt_voc = stmt_voc.where(models.VocListHH.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_where_and.append(models.VocListHH.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_where_and.append(models.VocListHH.new_center_nm.in_(txt_l))
    elif code == "팀별":
        pass
        # stmt_where_and.append(models.VocListHH.oper_team_nm.in_(txt_l))
    elif code== "조별":
        pass
        # stmt_where_and.append(models.VocListHH.area_jo_nm.in_(txt_l))
        # stmt_where_and.append(models.VocListHH.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where_and.append(models.VocListHH.sido_nm.in_(txt_l))
    elif code == "시군구별":
        pass
        stmt_where_and.append(models.VocListHH.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_where_and.append(models.VocListHH.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx
    stmt_voc = stmt_voc.where(and_(*stmt_where_and))

    # 상품 조건
    stmt_voc = stmt_voc.where(models.VocListHH.anals_3_prod_level_nm.in_(["5G","LTE"]))

    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    query_keys = query.keys()
    result = schemas.VocSummaryOutput(**dict(*query_result))

    #전국건수 query
    g5_voc_cnt = func.sum(case([(models.VocListHH.anals_3_prod_level_nm == '5G', 1)], else_=0)).label("g5_all_cnt")
    lte_voc_cnt = func.sum(case([(models.VocListHH.anals_3_prod_level_nm == 'LTE', 1)], else_=0)).label("lte_all_cnt")
    stmt_voc = select(models.VocListHH.base_date.label("date"), g5_voc_cnt, lte_voc_cnt)

    # 기간
    if start_date:
        stmt_voc = stmt_voc.where(models.VocListHH.base_date == start_date)
    # 상품 조건
    stmt_voc = stmt_voc.where(models.VocListHH.anals_3_prod_level_nm.in_(["5G","LTE"]))
    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()
    result.g5_all_cnt = dict(*query_result)["g5_all_cnt"]
    result.lte_all_cnt = dict(*query_result)["lte_all_cnt"]
    # 비율
    result.g5_all_ratio = round(result.g5_voc/result.g5_all_cnt*100, 2) if result.g5_all_cnt else 0
    result.lte_all_ratio = round(result.lte_voc/result.lte_all_cnt*100, 2) if result.lte_all_cnt else 0

    ## 전주, 전전주
    stmt_where_and = []
    a_week_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")
    two_weeks_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(14)).strftime("%Y%m%d")
    g5_a_voc_cnt = func.sum(case([(and_(models.VocList.base_date == a_week_ago,
                                        models.VocList.anals_3_prod_level_nm == "5G",
                                        ), 1)
                                  ], else_=0)).label("g5_a_week_ago")
    g5_two_voc_cnt = func.sum(case([(and_(models.VocList.base_date == two_weeks_ago,
                                          models.VocList.anals_3_prod_level_nm == "5G",
                                          ), 1)
                                    ], else_=0)).label("g5_two_weeks_ago")
    lte_a_voc_cnt = func.sum(case([(and_(models.VocList.base_date == a_week_ago,
                                         models.VocList.anals_3_prod_level_nm == "LTE",
                                         ), 1)
                                   ], else_=0)).label("lte_a_week_ago")
    lte_two_voc_cnt = func.sum(case([(and_(models.VocList.base_date == two_weeks_ago,
                                           models.VocList.anals_3_prod_level_nm == "LTE",
                                           ), 1)
                                     ], else_=0)).label("lte_two_weeks_ago")
    stmt_voc = select(g5_a_voc_cnt, g5_two_voc_cnt, lte_a_voc_cnt, lte_two_voc_cnt)

    # 기간
    if start_date:
        stmt_voc = stmt_voc.where(models.VocList.base_date.in_([a_week_ago, two_weeks_ago]))
    # 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.VocList.mkng_cmpn_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_where_and.append(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_where_and.append(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_where_and.append(models.VocList.oper_team_nm.in_(txt_l))
    elif code== "조별":
        stmt_where_and.append(models.VocList.area_jo_nm.in_(txt_l))
        stmt_where_and.append(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where_and.append(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        pass
        stmt_where_and.append(models.VocList.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_where_and.append(models.VocList.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx
    stmt_voc = stmt_voc.where(and_(*stmt_where_and))
    # 상품 조건
    stmt_voc = stmt_voc.where(models.VocList.anals_3_prod_level_nm.in_(['5G','LTE']))

    # print(stmt_voc.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt_voc)
    query_result = query.all()

    g5_a_week_ago = dict(*query_result)["g5_a_week_ago"]
    g5_two_weeks_ago = dict(*query_result)["g5_two_weeks_ago"]
    lte_a_week_ago = dict(*query_result)["lte_a_week_ago"]
    lte_two_weeks_ago = dict(*query_result)["lte_two_weeks_ago"]

    result.g5_compare_1w = result.g5_voc - g5_a_week_ago if g5_a_week_ago else 0
    result.g5_compare_2w = result.g5_voc - g5_two_weeks_ago if g5_two_weeks_ago else 0
    result.lte_compare_1w = result.lte_voc - lte_a_week_ago if lte_a_week_ago else 0
    result.lte_compare_2w = result.lte_voc - lte_two_weeks_ago if lte_two_weeks_ago else 0

    return result


async def get_voc_spec_by_srno(db: AsyncSession, sr_tt_rcp_no: str = "", limit: int = 1000):
    # 1. voc상세
    """ VOC 상세를 제공하는 함수
        [ 파라미터 ]
        - sr_tt_rcp_no : T/T 접수번호
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
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
            bts_summary=[],
            inbldg_summary=[]
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
    # print(stmt_bts.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt_bts)

    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    bts_summary_list = list(map(lambda x: schemas.BtsSummary(**dict(zip(query_keys, x))), query_result))

    # 3 inbldg summary list ( by voc.base_date + voc.svc_cont_id )

    bldg_info = func.concat(models.MdtInbldg.bld_id," ",
                             models.MdtInbldg.tr_bld_name_dong," ",
                             models.MdtInbldg.bld_flr_desc).label("bldg_info")

    #rsrp 평균, 불량 , rsrq 불량
    bldg_sum_rsrp_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_rsrp_cnt,0)).label("bldg_rsrp_cnt")
    bldg_sum_rsrp_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_rsrp_sum,0)).label("bldg_rsrp_sum")
    bldg_sum_rsrp_m105d_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_rsrp_m105d_cnt,0)).label("bldg_rsrp_m105d_cnt")
    bldg_sum_rsrp_m110d_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_rsrp_m110d_cnt,0)).label("bldg_rsrp_m110d_cnt")
    bldg_sum_rsrp_bad_cnt = func.sum(
                                func.ifnull(models.MdtInbldg.bldg_rsrp_m105d_cnt, 0)
                                + func.ifnull(models.MdtInbldg.bldg_rsrp_m110d_cnt, 0)
                        ).label("bldg_rsrp_bad_cnt")

    # rip 평균, 불량
    bldg_sum_rip_maxd_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_new_rip_maxd_cnt, 0)).label("bldg_rip_maxd_cnt")
    bldg_sum_rip_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_rip_sum, 0)).label("bldg_rip_sum")
    bldg_sum_rip_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_rip_cnt, 0)).label("bldg_rip_cnt")

    # phr 평균, 불량
    bldg_sum_phr_m3d_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_new_phr_m3d_cnt, 0)).label("bldg_phr_m3d_cnt")
    bldg_sum_phr_mind_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_new_phr_mind_cnt, 0)).label("bldg_phr_mind_cnt")
    bldg_sum_phr_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_phr_sum,0)).label("bldg_phr_sum")
    bldg_sum_phr_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_phr_cnt,0)).label("bldg_phr_cnt")
    bldg_sum_phr_bad_cnt = func.sum(
                            func.ifnull(models.MdtInbldg.bldg_new_phr_m3d_cnt, 0)
                            + func.ifnull(models.MdtInbldg.bldg_new_phr_mind_cnt, 0)
                        ).label("bldg_phr_bad_cnt")

    #nr_rsrp
    bldg_sum_nr_rsrp_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_nr_rsrp_cnt, 0)).label("bldg_nr_rsrp_cnt")
    bldg_sum_nr_rsrp_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_nr_rsrp_sum, 0)).label("bldg_nr_rsrp_sum")

    #nsinr
    bldg_sum_nsinr_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_nsinr_cnt, 0)).label("bldg_nsinr_cnt")
    bldg_sum_nsinr_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_nsinr_sum, 0)).label("bldg_nsinr_sum")

    #rscp
    bldg_sum_rscp_bad_cnt = func.sum(
                            func.ifnull(models.MdtInbldg.bldg_rscp_0_m105d_cnt, 0)
                            + func.ifnull(models.MdtInbldg.bldg_rscp_0_m100d_cnt, 0)
                        ).label("bldg_rscp_bad_cnt")
    bldg_sum_rscp_cnt = func.sum(func.ifnull(models.MdtInbldg.bldg_rscp_cnt, 0)).label("bldg_rscp_cnt")
    bldg_sum_rscp_sum = func.sum(func.ifnull(models.MdtInbldg.bldg_rscp_sum, 0)).label("bldg_rscp_sum")

    entities_inbldg = [
        models.MdtInbldg.base_date,  # label("기준년원일"),
        models.MdtInbldg.svc_cont_id,
        models.MdtInbldg.bld_id,
        models.MdtInbldg.addr_div,
        bldg_info,
        models.MdtInbldg.bld_flr_desc,
        models.MdtInbldg.adr_utmkx,
        models.MdtInbldg.adr_utmky,
    ]
    entities_inbldg_groupby = [
        bldg_sum_rsrp_m105d_cnt,    # rsrp불량(-109~-105)
        bldg_sum_rsrp_m110d_cnt,    # rsrp불량(min~-110)
        bldg_sum_rsrp_bad_cnt,       # rsrp불량
        bldg_sum_rsrp_cnt,           # rsrp
        bldg_sum_rsrp_sum,           # rsrp
        bldg_sum_rip_maxd_cnt,       # rip 불량(-091.9~max)
        bldg_sum_rip_sum,            # rip 합
        bldg_sum_rip_cnt,            # rip 건수
        bldg_sum_phr_m3d_cnt,        # phr m3d (-3~0.9)
        bldg_sum_phr_mind_cnt,       # phr mind (min~-3.1 )
        bldg_sum_phr_bad_cnt,        # phr 불량
        bldg_sum_phr_sum,            # phr
        bldg_sum_phr_cnt,            # phr
        bldg_sum_nr_rsrp_cnt,
        bldg_sum_nr_rsrp_sum,
        bldg_sum_nsinr_cnt,
        bldg_sum_nsinr_sum,
        bldg_sum_rscp_bad_cnt,
        bldg_sum_rscp_sum,
        bldg_sum_rscp_cnt,
    ]

    stmt_inbldg = select(*entities_inbldg, *entities_inbldg_groupby)
    ref_day = (datetime.strptime(voc_user_info.base_date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
    stmt_inbldg = stmt_inbldg.where(between(models.MdtInbldg.base_date, ref_day, voc_user_info.base_date))
    stmt_inbldg = stmt_inbldg.where(models.MdtInbldg.svc_cont_id == voc_user_info.svc_cont_id)
    stmt_inbldg = stmt_inbldg.group_by(*entities_inbldg).order_by(bldg_sum_rsrp_bad_cnt.desc())
    query = await db.execute(stmt_inbldg)
    # print(stmt_inbldg.compile(compile_kwargs={"literal_binds": True}))

    query_result = query.fetchmany(size=limit)
    query_keys = query.keys()

    inbldg_summary_list = list(map(lambda x: schemas.InbldgSummary(**dict(zip(query_keys, x))), query_result))

    return schemas.VocSpecOutput(
        voc_user_info=voc_user_info,
        bts_summary=bts_summary_list,
        inbldg_summary=inbldg_summary_list,
    )


async def get_voc_trend_item_by_group_date(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                           by:str="code", start_date: str = None, end_date: str = None):
    """ 일자별 VOC 트랜드를 제공하는 함수
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - by :
        - start_date :  조회기간(시작일자, 예: 20230201)
        - end_date :  조회기간(종료일자, 예: 20230229)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    where_ins = []  # code테이블, volte 테이블 where in (a, b, c)
    stmt_where_and = []  # where list

    # 집계항목
    voc_cnt = func.count(models.VocList.sr_tt_rcp_no_cnt).label("voc_cnt")

    # where
    ## 기간조건
    if not start_date:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    if not end_date:
        end_date = start_date

    stmt_where_and.append(between(models.VocList.base_date, start_date, end_date))

    ## 상품 조건
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(models.VocList.anals_3_prod_level_nm.in_(prod_l))
        prod_column = models.VocList.anals_3_prod_level_nm
    else:
        prod_column = models.VocList.anals_3_prod_level_nm

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "제조사별":
        stmt_where_and.append(models.VocList.mkng_cmpn_nm.in_(where_ins))
        code_column = models.VocList.mkng_cmpn_nm
    elif code == "본부별":
        where_ins = [txt.replace("NW운용본부", "") for txt in where_ins]
        stmt_where_and.append(models.VocList.new_hq_nm.in_(where_ins))
        code_column = models.VocList.new_hq_nm

    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        stmt_where_and.append(models.VocList.new_center_nm.in_(where_ins))
        code_column = models.VocList.new_center_nm

    elif code == "팀별":
        stmt_where_and.append(models.VocList.oper_team_nm.in_(where_ins))
        code_column = models.VocList.oper_team_nm

    elif code == "조별":
        stmt_where_and.append(models.VocList.oper_team_nm != "지하철엔지니어링부")
        stmt_where_and.append(models.VocList.area_jo_nm.in_(where_ins))
        code_column = models.VocList.area_jo_nm

    elif code == "시도별":
        stmt_where_and.append(models.VocList.sido_nm.in_(where_ins))
        code_column = models.VocList.sido_nm

    elif code == "시군구별":
        stmt_where_and.append(models.VocList.gun_gu_nm.in_(where_ins))
        code_column = models.VocList.gun_gu_nm

    elif code == "읍면동별":
        stmt_where_and.append(models.VocList.eup_myun_dong_nm.in_(where_ins))
        code_column = models.VocList.eup_myun_dong_nm

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
        models.VocList.base_date.label("date"),
        voc_cnt
    ).where(
        and_(*stmt_where_and)
    ).group_by(models.VocList.base_date,
               by_column)

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result = query_cut.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.VocTrendOutput(date=r[1], value=r[2]) for r in query_result if r[0] == code]
        list_items.append(schemas.VocTrendItemOutput(title=code, data=t_l))

    return list_items


# 조기준X
async def get_voc_trend_by_group_month(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                 start_month: str = None, end_month: str = None):
    """ 월별 VOC 트랜드를 제공하는 함수 - 폐기 예정 (월별 VOC 트랜드 통합) : get_voc_trend_item_by_group_month
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_month :  조회기간(시작일자, 예: 202302)
        - end_month :  조회기간(종료일자, 예: 202302)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
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
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.new_hq_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터","") for txt in txt_l]
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.new_center_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.new_center_nm.in_(txt_l))
    elif code == "팀별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.oper_team_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.oper_team_nm.in_(txt_l))
    elif code == "시도별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.sido_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.sido_nm.in_(txt_l))
    elif code == "시군구별":
        stmt_sbscr = stmt_sbscr.where(models.SubscrMM.gun_gu_nm.in_(txt_l))
        stmt_voc = stmt_voc.where(models.VocListMM.gun_gu_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

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
                                           by: str="code", start_month: str = None, end_month: str = None):
    """ 월별 VOC 트랜드를 제공하는 함수
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - by : 기본값: "code"
        - start_month :  조회기간(시작일자, 예: 202302)
        - end_month :  조회기간(종료일자, 예: 202302)
        - limit : 데이터 조회제약 건수
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    where_ins = []  # code테이블, voc 테이블 where in (a, b, c)
    sbscr_where_and = [] # sbscr table where list
    voc_where_and = []  # voc table where list

    # 집계항목
    voc_cnt = func.count(models.VocListMM.sr_tt_rcp_no).label("voc_cnt")
    sbscr_cnt = func.sum(models.SubscrMM.bprod_maint_sbscr_cascnt).label("sbscr_cnt")

    # where
    ## 기간조건
    if not start_month:
        start_month = (datetime.now() - timedelta(days=1)).strftime('%Y%m')
    if not end_month:
        end_month = start_month

    sbscr_where_and.append(between(models.SubscrMM.base_ym, start_month, end_month))
    voc_where_and.append(between(models.VocListMM.base_ym, start_month, end_month))

    ## 상품 조건
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        sbscr_where_and.append(models.SubscrMM.anals_3_prod_level_nm.in_(prod_l))
        voc_where_and.append(models.VocListMM.anals_3_prod_level_nm.in_(prod_l))
        v_prod_column = models.VocListMM.anals_3_prod_level_nm
        s_prod_column = models.SubscrMM.anals_3_prod_level_nm
    else:
        v_prod_column = models.VocListMM.anals_3_prod_level_nm
        s_prod_column = models.SubscrMM.anals_3_prod_level_nm

    ## code의 값목록 : 삼성|노키아
    if group != '':
        where_ins = group.split("|")

    ## 선택 조건
    if code == "본부별":
        where_ins = [txt.replace("NW운용본부","") for txt in where_ins]
        sbscr_sel_nm = models.SubscrMM.new_hq_nm
        voc_sel_nm = models.VocListMM.new_hq_nm  # voc 테이블 select 변수

        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))
        voc_where_and.append(voc_sel_nm.in_(where_ins))
    elif code == "센터별":
        where_ins = [txt.replace("액세스운용센터","") for txt in where_ins]
        sbscr_sel_nm = models.SubscrMM.new_center_nm
        voc_sel_nm = models.VocListMM.new_center_nm  # voc 테이블 select 변수

        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))
        voc_where_and.append(voc_sel_nm.in_(where_ins))
    elif code == "팀별":
        sbscr_sel_nm = models.SubscrMM.oper_team_nm
        voc_sel_nm = models.VocListMM.oper_team_nm  # voc 테이블 select 변수

        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))
        voc_where_and.append(voc_sel_nm.in_(where_ins))
    elif code == "시도별":
        sbscr_sel_nm = models.SubscrMM.sido_nm
        voc_sel_nm = models.VocListMM.sido_nm  # voc 테이블 select 변수

        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))
        voc_where_and.append(voc_sel_nm.in_(where_ins))
    elif code == "시군구별":
        sbscr_sel_nm = models.SubscrMM.gun_gu_nm
        voc_sel_nm = models.VocListMM.gun_gu_nm  # voc 테이블 select 변수

        sbscr_where_and.append(sbscr_sel_nm.in_(where_ins))
        voc_where_and.append(voc_sel_nm.in_(where_ins))
    elif code == "전국" or code =="전체" or code =="all":
        sbscr_sel_nm = literal("all")
        voc_sel_nm = literal("all")
    else:
        raise ex.ex.NotFoundAccessKeyEx

    # group by
    if by == "prod":
        s_by_column = s_prod_column
        v_by_column = v_prod_column
    elif by == "code":
        s_by_column = sbscr_sel_nm
        v_by_column = voc_sel_nm
    elif by == "all":
        s_by_column = literal("")
        v_by_column = literal("")
    else:
        s_by_column = sbscr_sel_nm
        v_by_column = voc_sel_nm

    # stmt 생성
    ## sbscr sql select
    st_sbscr = select(
        s_by_column.label("code"),
        models.SubscrMM.base_ym,
        sbscr_cnt
    ).where(
        and_(*sbscr_where_and)
    ).group_by(models.SubscrMM.base_ym, s_by_column)

    ## voc sql select
    st_voc = select(
        models.VocListMM.base_ym,
        v_by_column.label("code"),
        voc_cnt
    ).where(
        and_(*voc_where_and)
    ).group_by(
        models.VocListMM.base_ym,
        v_by_column
    ).subquery()

    ## sbscr + voc join
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
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query_cut = await db.execute(stmt)
    query_result = query_cut.all()

    code_set = set([r[0] for r in query_result])
    list_items = []
    for code in code_set:
        t_l = [schemas.VocTrendMonthOutput(**r) for r in query_result if r[0] == code]
        list_items.append(schemas.VocTrendItemMonthOutput(title=code, data=t_l))

    return list_items

#시간대별 VOC추이
async def get_voc_trend_by_group_hour_stack(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                 start_date: str = None):
    """ XXXX를 제공하는 함수
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    ## CODE_HOUR.hh left outer join voctbl
    today = datetime.today().strftime("%Y%m%d")
    if not start_date:
        start_date = today

    # 기간
    if start_date == today:
        today_tbl_name = models.VocListHH
    else:
        today_tbl_name = models.VocList

    # 당일 시간별 voc
    today_voc_cnt = func.count(func.ifnull(today_tbl_name.sr_tt_rcp_no, 0)).label("value")
    today_voc_hour = func.substring(today_tbl_name.sr_tt_rcp_no, 11, 2).label("hour")
    today_stmt_voc = select(today_voc_hour, today_voc_cnt)
    today_stmt_voc = today_stmt_voc.where(today_tbl_name.base_date == start_date)

    # 전주,전전주 시간별 voc
    voc_cnt = func.count(func.ifnull(models.VocList.sr_tt_rcp_no, 0)).label("value")
    voc_hour = func.substring(models.VocList.sr_tt_rcp_no, 11, 2).label("hour")
    a_week_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(7)).strftime("%Y%m%d")
    two_weeks_ago = (datetime.strptime(start_date, "%Y%m%d") - timedelta(14)).strftime("%Y%m%d")

    stmt_voc_1 = select(voc_hour, voc_cnt)
    stmt_voc_1 = stmt_voc_1.where(models.VocList.base_date == a_week_ago)

    stmt_voc_2 = select(voc_hour, voc_cnt)
    stmt_voc_2 = stmt_voc_2.where(models.VocList.base_date == two_weeks_ago)

    txt_l = []
    if group != "":
        txt_l = group.split("|")

    # 선택 조건
    if code == "제조사별":
        pass
        # today_stmt_voc = today_stmt_voc.where(today_tbl_name.mkng_cmpn_nm.in_(txt_l))
        # stmt_voc_1 = stmt_voc_1.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
        # stmt_voc_2 = stmt_voc_2.where(models.VocList.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부","") for txt in txt_l]
        today_stmt_voc = today_stmt_voc.where(today_tbl_name.new_hq_nm.in_(txt_l))
        stmt_voc_1 = stmt_voc_1.where(models.VocList.new_hq_nm.in_(txt_l))
        stmt_voc_2 = stmt_voc_2.where(models.VocList.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        today_stmt_voc = today_stmt_voc.where(today_tbl_name.new_center_nm.in_(txt_l))
        stmt_voc_1 = stmt_voc_1.where(models.VocList.new_center_nm.in_(txt_l))
        stmt_voc_2 = stmt_voc_2.where(models.VocList.new_center_nm.in_(txt_l))
    elif code == "팀별":
        today_stmt_voc = today_stmt_voc.where(today_tbl_name.oper_team_nm.in_(txt_l))
        stmt_voc_1 = stmt_voc_1.where(models.VocList.oper_team_nm.in_(txt_l))
        stmt_voc_2 = stmt_voc_2.where(models.VocList.oper_team_nm.in_(txt_l))
    elif code== "조별":
        pass
        # today_stmt_voc = today_stmt_voc.where(today_tbl_name.area_jo_nm.in_(txt_l))
        # stmt_voc_1 = stmt_voc_1.where(models.VocList.area_jo_nm.in_(txt_l))
        # stmt_voc_2 = stmt_voc_2.where(models.VocList.area_jo_nm.in_(txt_l))
        #
        # today_stmt_voc = today_stmt_voc.where(today_tbl_name.oper_team_nm != "지하철엔지니어링부")
        # stmt_voc_1 = stmt_voc_1.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
        # stmt_voc_2 = stmt_voc_2.where(models.VocList.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        today_stmt_voc = today_stmt_voc.where(today_tbl_name.sido_nm.in_(txt_l))
        stmt_voc_1 = stmt_voc_1.where(models.VocList.sido_nm.in_(txt_l))
        stmt_voc_2 = stmt_voc_2.where(models.VocList.sido_nm.in_(txt_l))
    elif code == "시군구별":
        pass
        # today_stmt_voc = today_stmt_voc.where(today_tbl_name.gun_gu_nm.in_(txt_l))
        # stmt_voc_1 = stmt_voc_1.where(models.VocList.gun_gu_nm.in_(txt_l))
        # stmt_voc_2 = stmt_voc_2.where(models.VocList.gun_gu_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # 상품 조건
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        today_stmt_voc = today_stmt_voc.where(today_tbl_name.anals_3_prod_level_nm.in_(prod_l))
        stmt_voc_1 = stmt_voc_1.where(models.VocList.anals_3_prod_level_nm.in_(prod_l))
        stmt_voc_2 = stmt_voc_2.where(models.VocList.anals_3_prod_level_nm.in_(prod_l))

    today_stmt_voc = today_stmt_voc.group_by(today_voc_hour).subquery()
    stmt_voc_1 = stmt_voc_1.group_by(voc_hour).subquery()
    stmt_voc_2 = stmt_voc_2.group_by(voc_hour).subquery()

    stmt = select(
            models.CodeHour.hh.label("hour"),
            func.ifnull(today_stmt_voc.c.value, 0).label("today_cnt"),
            func.ifnull(stmt_voc_1.c.value, 0).label("a_week_ago_cnt"),
            func.ifnull(stmt_voc_2.c.value, 0).label("two_weeks_ago_cnt")
    ).outerjoin(
            today_stmt_voc,
            today_stmt_voc.c.hour == models.CodeHour.hh
        ).outerjoin(
            stmt_voc_1,
            stmt_voc_1.c.hour == models.CodeHour.hh
        ).outerjoin(
            stmt_voc_2,
            stmt_voc_2.c.hour == models.CodeHour.hh
        )

    # print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_voc_trend = list(map(lambda x: schemas.VocHourTrendOutput(**dict(zip(query_keys, x))), query_result))

    for i in range(1, len(list_voc_trend)):
        list_voc_trend[i].today_cnt += list_voc_trend[i-1].today_cnt
        list_voc_trend[i].a_week_ago_cnt += list_voc_trend[i-1].a_week_ago_cnt
        list_voc_trend[i].two_weeks_ago_cnt += list_voc_trend[i-1].two_weeks_ago_cnt

    return list_voc_trend


async def get_voc_count_item_by_group_hour(db: AsyncSession, prod: str = None, code: str = None, group: str = None,
                                         start_date: str = None, by: str = None):
    """ XXXX를 제공하는 함수
        [ 파라미터 ]
        - prod : 5G, LTE, 3G
        - code : 센터별, 전국, 본부별, 팀별, 조별
        - group :
        - start_date :  조회기간(시작일자, 예: 20230201)
        - end_date :  조회기간(종료일자, 예: 20230229)
        - by :
        [ 반환값 ]
        [ 관련 테이블 ]
    """
    ## def : 아이템별 VOC건수 heatmap용 (시간별) 
    stmt_where_and = []

    # start_Date가 없으면 당일로 조회
    today = datetime.today().strftime("%Y%m%d")
    if not start_date : 
        start_date = today

    # from : tbl_name은 today는 실시간Tbl 참조, 과거는 SUM_VOC_TXN 참조
    if start_date == today:
        tbl_name = models.VocListHH
    else:
        tbl_name = models.VocList

    # 계산값 : VOC건수
    voc_cnt = func.count(func.ifnull(tbl_name.sr_tt_rcp_no, 0)).label("voc_cnt")

    # x축 : hour
    voc_hour = func.substring(tbl_name.sr_tt_rcp_no, 11, 2).label("hour")

    # y축 : by
    if by == "유형대":
        grp_col = tbl_name.voc_wjt_scnd_nm
    elif by == "유형중":
        grp_col = tbl_name.voc_wjt_tert_nm
    elif by == "유형소":
        grp_col = tbl_name.voc_wjt_qrtc_nm
    elif by == "SA구분":
        grp_col = tbl_name.sa_5g_suprt_div_nm
    elif by  == "단말기종":
        grp_col = tbl_name.hndset_pet_nm
    elif by == "시군구":
        grp_col = tbl_name.gun_gu_nm
    else :
        grp_col = tbl_name.voc_wjt_scnd_nm

    # where : prod + code + group+ start_date+ end_date
    ## 날짜 조건
    stmt_where_and.append(tbl_name.base_date == start_date)
    ## 상품 조건
    if prod and prod != "전체" and prod != "all":
        prod_l = prod.split("|")
        stmt_where_and.append(tbl_name.anals_3_prod_level_nm.in_(prod_l))

    ## 선택조건(code+ group)
    txt_l = []
    ## code의 값목록 : 삼성|노키아
    if group != "":
        txt_l = group.split("|")

    if code == "제조사별":
        pass
        # stmt_where_and.append(tbl_name.mkng_cmpn_nm.in_(txt_l))
        # stmt_voc = stmt_voc.where(tbl_name.mkng_cmpn_nm.in_(txt_l))
    elif code == "본부별":
        txt_l = [txt.replace("NW운용본부", "") for txt in txt_l]
        stmt_where_and.append(tbl_name.new_hq_nm.in_(txt_l))
    elif code == "센터별":
        txt_l = [txt.replace("액세스운용센터", "") for txt in txt_l]
        stmt_where_and.append(tbl_name.new_center_nm.in_(txt_l))
    elif code == "팀별":
        pass
        # stmt_where_and.append(tbl_name.oper_team_nm.in_(txt_l))
    elif code == "조별":
        pass
        # stmt_where_and.append(tbl_name.area_jo_nm.in_(txt_l))
        # stmt_where_and.append(models.tbl_name.oper_team_nm != "지하철엔지니어링부")
    elif code == "시도별":
        stmt_where_and.append(tbl_name.sido_nm.in_(txt_l))
    elif code == "시군구별":
        pass
        stmt_where_and.append(tbl_name.gun_gu_nm.in_(txt_l))
    elif code == "읍면동별":
        stmt_where_and.append(tbl_name.eup_myun_dong_nm.in_(txt_l))
    elif code == "전국" or code =="전체" or code =="all":
        pass
    else:
        raise ex.NotFoundAccessKeyEx

    # stmt 생성
    entities = [
        grp_col.label("name"),
        voc_hour,
    ]
    entities_groupby = [
        voc_cnt
    ]
    stmt = select(*entities, *entities_groupby)
    stmt = stmt.where(and_(*stmt_where_and))
    stmt = stmt.group_by(*entities)

    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    query = await db.execute(stmt)
    query_result = query.fetchall()
    # output , [{name:분류명, data:[0시건수,01시건수,02시건수,... ]}, {name:b, data:[0,0,0,0] }, ]

    list_items = []
    code_set = set([r[0] for r in query_result])
    for code in code_set:
        dict_hour = {str(x).zfill(2): 0 for x in range(24)}
        for r in query_result :
            if r[0] == code:
                dict_hour[r[1]] = r[2]
        list_items.append(schemas.VocHourTrendItemOutput(name=code, data=list(dict_hour.values())))

    return list_items
