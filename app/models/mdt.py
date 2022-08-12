from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Mdt(KBase):
    __tablename__ = "mdt"

    base_ym = Column(String(100))
    year_base_week_nm = Column(String(100))
    base_date = Column(String(100), primary_key=True)
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    bts_maker_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
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
