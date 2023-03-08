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
    __tablename__ = "SUM_VOC_TXN"

    base_ym = Column(String(100))
    year_base_week_nm = Column(String(100))
    base_date = Column(String(100))
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    equip_cd = Column(String(100))
    equip_nm = Column(String(100))
    latit_val = Column(String(50))
    lngit_val = Column(String(50))
    anals_3_prod_level_nm = Column(String(100))
    bprod_nm = Column(String(100))
    hndset_pet_nm = Column(String(100))
    sa_5g_suprt_div_nm = Column(String(100))
    voc_type_nm = Column(String(100))
    voc_wjt_prmr_nm = Column(String(100))
    voc_wjt_scnd_nm = Column(String(100))
    voc_wjt_tert_nm = Column(String(100))
    voc_wjt_qrtc_nm = Column(String(100))
    sr_tt_rcp_no = Column(String(100), primary_key=True)
    svc_cont_id = Column(String(100))
    trobl_rgn_broad_sido_nm = Column(String(100))
    trobl_rgn_sgg_nm = Column(String(100))
    trobl_rgn_eup_myun_dong_li_nm = Column(String(100))
    trobl_rgn_dtl_sbst = Column(String(100))
    utmkx = Column(String(20))
    utmky = Column(String(20))
    day_utmkx = Column(String(20))
    day_utmky = Column(String(20))
    ngt_utmkx = Column(String(20))
    ngt_utmky = Column(String(20))
    voc_rcp_txn = Column(String(1000))
    tt_trt_sbst = Column(String(1000))
    voc_actn_txn = Column(String(1000))
    equip_cd_data = Column(String(100))
    equip_nm_data = Column(String(100))
    latit_val_data = Column(String(50))
    lngit_val_data = Column(String(50))

    sr_tt_rcp_no_cnt = Column(Integer)

    new_hq_nm = Column(String(100))
    new_center_nm = Column(String(100))


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
    hndset_pet_nm = Column(String(100))                     # (K)단말기별칭명
    mf_cd_nm = Column(String(50))                   # 단말SW MF코드명
    bss_org_nm = Column(String(20))                 # VOC 접수자조직
    emp_bizr_nm = Column(String(20))                # VOC 접수자(실시간)
    biz_hq_nm = Column(String(100))                 # 기지국사업본부(신주사용지지국01(음성(월)))
    leg_sido_nm = Column(String(100))               # 법정시도(주사용기지국01(음성(월)))
    leg_gun_gu_nm = Column(String(100))             # 법정군구(주사용기지국01(음성(월)))
    leg_dong_nm = Column(String(100))               # 법정동(주사용기지국01(음성(월)))
    equip_nm = Column(String(100))                  # 주사용기지국명(주사용기지국01(음성(월)))
    equip_nm_rt = Column(String(100))               # 기지국명(F)(실시간주사용기지국01(음성))
    anals_3_prod_level_nm = Column(String(100))     # 분석상품레벨3
    sido_nm = Column(String(100))                   # 시도명
    gun_gu_nm = Column(String(100))                 # 구군명
    eup_myun_dong_nm = Column(String(100))          # 읍면동명
    trobl_bas_adr =Column(String(150))              # 장애기본주소
    trobl_dtl_adr =Column(String(150))              # 장애상세주소
    adm_sido_nm = Column(String(100))               # 행정시도(주사용기지국01(음성(월)))
    adm_gun_gu_nm = Column(String(100))             # 행정군구(주사용기지국01(음성(월)))
    adm_dong_nm = Column(String(100))               # 행정동(주사용기지국01(음성(월)))
    sa_5g_suprt_div_nm = Column(String(50))         # 5G SA/NSA 지원구분
    latit_val_rt = Column(String(100))              # 위도값(실시간주사용기지국01(음성))
    lngit_val_rt = Column(String(100))              # 경도값(실시간주사용기지국01(음성))
    latit_val = Column(String(100))                 # 위도값(주사용기지국01(음성(월)))
    lngit_val = Column(String(100))                 # 경도값(주사용기지국01(음성(월)))
    voc_rcp_txn = Column(String(1000))              # 상담처리내역(필터)
    sr_tt_rcp_no_cnt = Column(Integer)              # VOC접수건수
    mkng_cmpn_nm = Column(String(100))              # 제조회사명
    oper_team_nm = Column(String(100))              # 운용팀명
    equip_cd = Column(String(100))                  # 장비번호
    area_hq_nm = Column(String(100))                # 최적화본부명 - 지역 H/Q명
    area_center_nm = Column(String(100))            # 최적화센터명 - 지역 센터명
    area_team_nm = Column(String(100))              # 최적화팀명 - 지역 팀명
    area_jo_nm = Column(String(100))                # 최적화조명 - 지역 조명

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
    __tablename__ = "SUM_VOC_DTL_TXN"

    base_date = Column(String(100), primary_key=True)
    svc_cont_id = Column(String(100), primary_key=True)
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
    latit_val = Column(String(50))
    lngit_val = Column(String(50))
    cell_cd = Column(String(50))
    s1ap_cnt = Column(Integer)
    s1ap_fail_cnt = Column(Integer)
    rsrp_m105d_cnt = Column(Integer)
    rsrp_m110d_cnt = Column(Integer)
    rsrp_cnt = Column(Integer)
    rsrp_sum = Column(Integer)
    rsrq_m15d_cnt = Column(Integer)
    rsrq_m17d_cnt = Column(Integer)
    rsrq_cnt = Column(Integer)
    rsrq_sum = Column(Integer)
    new_rip_maxd_cnt = Column(Integer)
    rip_cnt = Column(Integer)
    rip_sum = Column(Integer)
    new_phr_m3d_cnt = Column(Integer)
    new_phr_mind_cnt = Column(Integer)
    phr_cnt = Column(Integer)
    phr_sum = Column(Integer)
    nr_rsrp_cnt = Column(Integer)
    nr_rsrp_sum = Column(Integer)
    volte_try_cacnt = Column(Integer)
    volte_comp_cacnt = Column(Integer)
    volte_self_fail_cacnt = Column(Integer)
    volte_other_fail_cacnt = Column(Integer)


class VocListMM(KBase):
    __tablename__ = "SUM_VOC_TXN_MM"

    base_ym = Column(String(6), primary_key=True)
    mkng_cmpn_nm = Column(String(50))
    biz_hq_cd = Column(String(20))
    biz_hq_nm = Column(String(50))
    oper_team_cd = Column(String(20))
    oper_team_nm = Column(String(50))
    area_hq_nm = Column(String(50))
    area_center_nm = Column(String(50))
    area_team_nm = Column(String(50))
    area_jo_nm = Column(String(50))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    anals_3_prod_level_nm = Column(String(50))
    bprod_nm = Column(String(50))
    hndset_pet_nm = Column(String(50))
    sa_5g_suprt_div_nm = Column(String(50))
    voc_type_nm = Column(String(20))
    voc_wjt_prmr_nm = Column(String(50))
    voc_wjt_scnd_nm = Column(String(50))
    voc_wjt_tert_nm = Column(String(50))
    voc_wjt_qrtc_nm = Column(String(50))
    new_hq_nm = Column(String(50))
    new_center_nm = Column(String(50))

    sr_tt_rcp_no = Column(Integer)