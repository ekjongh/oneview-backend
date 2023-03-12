########################################################################################################################
# VOC 서비스 모듈
#
# [ 테이블 리스트 ]
#   * SUM_VOC_TXN : VOC
#   * SUM_VOC_TXN_RTIME : VOC 실시간
#   * SUM_VOC_DTL_TXN : VOC 상세
#   * SUM_VOC_TXN_MM : VOC 월별누적
# ----------------------------------------------------------------------------------------------------------------------
# 2023.03.08 - 항목명 주석 추가
#
########################################################################################################################
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import KBase


class VocList(KBase):
    """ VOC (일단위 업데이트) """
    __tablename__ = "SUM_VOC_TXN"

    base_ym = Column(String(100))               # 기준년월
    year_base_week_nm = Column(String(100))     # 기준년주
    base_date = Column(String(100))             # 기준일자
    dow_nm = Column(String(100))                # 기준요일명
    wday_eweek_div_nm = Column(String(100))     # 평일휴일구분명
    mkng_cmpn_nm = Column(String(100))          # 제조사명
    biz_hq_nm = Column(String(100))             # 기지국사업본부
    oper_team_nm = Column(String(100))          # 운용팀
    area_hq_nm = Column(String(100))            # 최적화 본부명
    area_center_nm = Column(String(100))        # 최적화 센터명
    area_team_nm = Column(String(100))          # 최적화 팀명
    area_jo_nm = Column(String(100))            # 최적화 조명
    sido_nm = Column(String(100))               # 시도명
    gun_gu_nm = Column(String(100))             # 시군구명
    eup_myun_dong_nm = Column(String(100))      # 읍면동명
    equip_cd = Column(String(100))              # 국소ID
    equip_nm = Column(String(100))              # 지기국명
    latit_val = Column(String(50))              # 위도값
    lngit_val = Column(String(50))              # 경도값
    anals_3_prod_level_nm = Column(String(100)) # 분석상품 레벨3
    bprod_nm = Column(String(100))              # 기본상품
    hndset_pet_nm = Column(String(100))         # (K)단말기별칭명
    sa_5g_suprt_div_nm = Column(String(100))    # SA/NSA지원구분
    voc_type_nm = Column(String(100))           # VOC유형
    voc_wjt_prmr_nm = Column(String(100))       # 1차업무유형
    voc_wjt_scnd_nm = Column(String(100))       # 2차업무유형
    voc_wjt_tert_nm = Column(String(100))       # 3차업무유형
    voc_wjt_qrtc_nm = Column(String(100))       # 4차업무유형
    sr_tt_rcp_no = Column(String(100), primary_key=True)    # VOC접수번호
    svc_cont_id = Column(String(100))           # 서비스계약번호
    trobl_rgn_broad_sido_nm = Column(String(100))       # 장애 시도명
    trobl_rgn_sgg_nm = Column(String(100))              # 장애 시군구명
    trobl_rgn_eup_myun_dong_li_nm = Column(String(100)) # 장애 읍면동명
    trobl_rgn_dtl_sbst = Column(String(100))            # 장애 상세주소
    utmkx = Column(String(20))                  # 좌표X
    utmky = Column(String(20))                  # 좌표Y
    day_utmkx = Column(String(20))              # 주UTMK 좌표X
    day_utmky = Column(String(20))              # 주UTMK 좌표Y
    ngt_utmkx = Column(String(20))              # 야UTMK 좌표X
    ngt_utmky = Column(String(20))              # 야UTMK 좌표Y
    voc_rcp_txn = Column(String(1000))          # 상담처리내역
    tt_trt_sbst = Column(String(1000))          # 기술TT 조치내역
    voc_actn_txn = Column(String(1000))         # VOC조치내역
    equip_cd_data = Column(String(100))         # 국소ID 데이터
    equip_nm_data = Column(String(100))         # 국소명 데이터
    latit_val_data = Column(String(50))         # 위도값 데이터
    lngit_val_data = Column(String(50))         # 경도값 데이터

    sr_tt_rcp_no_cnt = Column(Integer)          # SR TT 접수번호건수

    new_hq_nm = Column(String(100))             # 본부명 신규구분
    new_center_nm = Column(String(100))         # 센터명 신규구분


class VocListHH(KBase):
    """ VOC 실시간 (20분단위 업데이트) """
    __tablename__ = "SUM_VOC_TXN_RTIME"

    base_date = Column(String(100))                         # 기준일자
    sr_tt_rcp_no = Column(String(100), primary_key=True)    # T/T접수번호
    svc_cont_id = Column("svc_cont_sorc_id", String(100))   # 서비스계약번호
    voc_wjt_prmr_nm = Column(String(100))                   # VOC 업무유형(1차) - 사용X
    voc_wjt_scnd_nm = Column(String(100))                   # VOC 업무유형(2차) - 유형대
    voc_wjt_tert_nm = Column(String(100))                   # VOC 업무유형(3차) - 유형중
    voc_wjt_qrtc_nm = Column(String(100))                   # VOC 업무유형(4차) - 유형소
    voc_type_nm = Column("voc_type_sorc_nm", String(100))   # VOC유형명
    hndset_pet_nm = Column(String(100))                     # (K)단말기별칭명 - 단말기종별
    mf_cd_nm = Column(String(50))                   # 단말SW MF코드명
    bss_org_nm = Column(String(20))                 # VOC 접수자조직
    emp_bizr_nm = Column(String(20))                # VOC 접수자(실시간)
    biz_hq_nm = Column(String(100))                 # 기지국사업본부(신주사용지지국01(음성(월))) - 센터별
    leg_sido_nm = Column(String(100))               # 법정시도(주사용기지국01(음성(월)))
    leg_gun_gu_nm = Column(String(100))             # 법정군구(주사용기지국01(음성(월)))
    leg_dong_nm = Column(String(100))               # 법정동(주사용기지국01(음성(월)))
    equip_nm = Column(String(100))                  # 주사용기지국명(주사용기지국01(음성(월)))
    equip_nm_rt = Column(String(100))               # 기지국명(F)(실시간주사용기지국01(음성))
    anals_3_prod_level_nm = Column(String(100))     # 분석상품레벨3
    sido_nm = Column(String(100))                   # 시도명부
    gun_gu_nm = Column(String(100))                 # 구군명
    eup_myun_dong_nm = Column(String(100))          # 읍면동명
    trobl_bas_adr =Column(String(150))              # 장애기본주소
    trobl_dtl_adr =Column(String(150))              # 장애상세주소
    adm_sido_nm = Column(String(100))               # 행정시도(주사용기지국01(음성(월)))
    adm_gun_gu_nm = Column(String(100))             # 행정군구(주사용기지국01(음성(월)))
    adm_dong_nm = Column(String(100))               # 행정동(주사용기지국01(음성(월)))
    sa_5g_suprt_div_nm = Column(String(50))         # 5G SA/NSA 지원구분 - SA구분별
    latit_val_rt = Column(String(100))              # 위도값(실시간주사용기지국01(음성))
    lngit_val_rt = Column(String(100))              # 경도값(실시간주사용기지국01(음성))
    latit_val = Column(String(100))                 # 위도값(주사용기지국01(음성(월)))
    lngit_val = Column(String(100))                 # 경도값(주사용기지국01(음성(월)))
    voc_rcp_txn = Column(String(1000))              # 상담처리내역(필터)
    sr_tt_rcp_no_cnt = Column(Integer)              # VOC접수건수
    mkng_cmpn_nm = Column(String(100))              # 제조회사명
    oper_team_nm = Column(String(100))              # 운용팀명 - 팀별
    equip_cd = Column(String(100))                  # 장비번호
    area_hq_nm = Column(String(100))                # 최적화본부명 - 지역 H/Q명 - 본부별 (WiNG기준 본부)
    area_center_nm = Column(String(100))            # 최적화센터명 - 지역 센터명 - 센터별 (WiNG기준 본부)
    area_team_nm = Column(String(100))              # 최적화팀명 - 지역 팀명 - 팀별 (WiNG기준 본부)
    area_jo_nm = Column(String(100))                # 최적화조명 - 지역 조명 - 조별 (WiNG기준 본부)

    # utmkx = Column(String(20))
    # utmky = Column(String(20))
    # day_utmkx = Column(String(20))
    # day_utmky = Column(String(20))
    # ngt_utmkx = Column(String(20))
    # ngt_utmky = Column(String(20))
    #
    # new_hq_nm = Column(String(50))
    # new_center_nm = Column(String(50))


    class Config:
        allow_population_by_field_name = True


class VocSpec(KBase):
    """ VOC 상세 (일단위 업데이트) """
    __tablename__ = "SUM_VOC_DTL_TXN"

    base_date = Column(String(100), primary_key=True)       # 기준일자
    svc_cont_id = Column(String(100), primary_key=True)     # 서비스계약번호
    mkng_cmpn_nm = Column(String(100))                      # 제조사
    biz_hq_nm = Column(String(100))                         # 기지국 사업본부
    oper_team_nm = Column(String(100))                      # 운용팀
    sido_nm = Column(String(100))                           # 시도명
    gun_gu_nm = Column(String(100))                         # 시군구명
    eup_myun_dong_nm = Column(String(100))                  # 읍면동명
    equip_cd = Column(String(100), primary_key=True)        # 국소ID
    equip_nm = Column(String(100))                          # 기지국명
    latit_val = Column(String(50))                          # 위도값
    lngit_val = Column(String(50))                          # 경도값
    cell_cd = Column(String(50))                            # 셀코드
    s1ap_cnt = Column(Integer)                              # S1AP 건수
    s1ap_fail_cnt = Column(Integer)                         # S1AP 실패건수
    rsrp_m105d_cnt = Column(Integer)                        # RSRP[-109~-105]건
    rsrp_m110d_cnt = Column(Integer)                        # RSRP[min~-110]건
    rsrp_cnt = Column(Integer)                  # RSRP건
    rsrp_sum = Column(Integer)                  # RSRP합계
    rsrq_m15d_cnt = Column(Integer)             # RSRQ[-16.5~-15]건
    rsrq_m17d_cnt = Column(Integer)             # RSRQ[min~-17]건
    rsrq_cnt = Column(Integer)                  # RSRQ건
    rsrq_sum = Column(Integer)                  # RSRQ합계
    new_rip_maxd_cnt = Column(Integer)          # RIP[-92~MAX]건
    rip_cnt = Column(Integer)                   # RIP건
    rip_sum = Column(Integer)                   # RIP합계
    new_phr_m3d_cnt = Column(Integer)           # PHR M3D건
    new_phr_mind_cnt = Column(Integer)          # PHR[min~-3.1]건
    phr_cnt = Column(Integer)                   # PHR건
    phr_sum = Column(Integer)                   # PHR합계
    nr_rsrp_cnt = Column(Integer)               # 5GRSRP건
    nr_rsrp_sum = Column(Integer)               # 5GRSRP합계
    volte_try_cacnt = Column(Integer)           # volte시도건수
    volte_comp_cacnt = Column(Integer)          # volte완료건수
    volte_self_fail_cacnt = Column(Integer)     # volte자체실패건수
    volte_other_fail_cacnt = Column(Integer)    # volte기타실패건수


class VocListMM(KBase):
    """ VOC 월누적 (일단위 업데이트) """
    __tablename__ = "SUM_VOC_TXN_MM"

    base_ym = Column(String(6), primary_key=True)   # 기준년월
    mkng_cmpn_nm = Column(String(50))               # 제조사
    biz_hq_cd = Column(String(20))                  # 기지국 사업본부
    biz_hq_nm = Column(String(50))                  # 기지국 사업본부명
    oper_team_cd = Column(String(20))               # 운용팀
    oper_team_nm = Column(String(50))               # 운용팀명
    area_hq_nm = Column(String(50))                 # 최적화 본부명
    area_center_nm = Column(String(50))             # 최적화 센터명
    area_team_nm = Column(String(50))               # 최적화 팀명
    area_jo_nm = Column(String(50))                 # 최적화 조명
    sido_nm = Column(String(100))                   # 시도명
    gun_gu_nm = Column(String(100))                 # 시군구명
    eup_myun_dong_nm = Column(String(100))          # 읍면동명
    anals_3_prod_level_nm = Column(String(50))      # 분석상품 레벨3
    bprod_nm = Column(String(50))                   # 기본상품
    hndset_pet_nm = Column(String(50))              # (K)단말기별칭명
    sa_5g_suprt_div_nm = Column(String(50))         # SA/NSA지원구분
    voc_type_nm = Column(String(20))                # VOC유형
    voc_wjt_prmr_nm = Column(String(50))            # 1차업무유형
    voc_wjt_scnd_nm = Column(String(50))            # 2차업무유형
    voc_wjt_tert_nm = Column(String(50))            # 3차업무유형
    voc_wjt_qrtc_nm = Column(String(50))            # 4차업무유형
    new_hq_nm = Column(String(50))                  # 본부명 (KPI)
    new_center_nm = Column(String(50))              # 센터명 (KPI)

    sr_tt_rcp_no = Column(Integer)                  # VOC접수번호