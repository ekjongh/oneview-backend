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
    __tablename__ = "SUM_VOC_TXN_RTIME"

    base_date = Column(String(100))
    sr_tt_rcp_no = Column(String(100), primary_key=True)
    svc_cont_id = Column("svc_cont_sorc_id", String(100))
    voc_wjt_prmr_nm = Column(String(100))
    voc_wjt_scnd_nm = Column(String(100))
    voc_wjt_tert_nm = Column(String(100))
    voc_wjt_qrtc_nm = Column(String(100))
    voc_type_nm = Column("voc_type_sorc_nm", String(100))
    hndset_pet_nm = Column(String(100))
    mf_cd_nm = Column(String(50))
    bss_org_nm = Column(String(20))
    emp_bizr_nm = Column(String(20))
    biz_hq_nm = Column(String(100))
    leg_sido_nm = Column(String(100))
    leg_gun_gu_nm = Column(String(100))
    leg_dong_nm = Column(String(100))
    equip_nm = Column(String(100))
    equip_nm_rt = Column(String(100))
    anals_3_prod_level_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    trobl_bas_adr =Column(String(150))
    trobl_dtl_adr =Column(String(150))
    adm_sido_nm = Column(String(100))
    adm_gun_gu_nm = Column(String(100))
    adm_dong_nm = Column(String(100))
    sa_5g_suprt_div_nm = Column(String(50))
    latit_val_rt = Column(String(100))
    lngit_val_rt = Column(String(100))
    latit_val = Column(String(100))
    lngit_val = Column(String(100))
    voc_rcp_txn = Column(String(1000))
    sr_tt_rcp_no_cnt = Column(Integer)
    mkng_cmpn_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    equip_cd = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))

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