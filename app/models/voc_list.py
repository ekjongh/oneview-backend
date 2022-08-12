from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class VocList(KBase):
    __tablename__ = "voc"

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
    voc_rcp_txn = Column(String(1000))
    tt_trt_sbst = Column(String(1000))
    voc_actn_txn = Column(String(1000))
    sr_tt_rcp_no_cnt = Column(Integer)
