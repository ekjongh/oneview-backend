from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from app.db.base_class import KBase


class Rrc(KBase):
    __tablename__ = "SUM_LTE_PRBUSAGE_DD"

    base_date = Column(String(100), primary_key=True)
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100), primary_key=True)
    prb_avg = Column(Float)
    rrc_att_sum = Column(Float)
    rrc_suces_sum = Column(Float)
    rrc_surces_rate_avg = Column(Float)



class RrcTrend(KBase):
    __tablename__ = "SUM_LTE_PRBUSAGE_TMP"

    base_date = Column(String(100), primary_key=True)
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100), primary_key=True)
    sum_prb_avg = Column(Float)
    cnt_prb_avg = Column(Float)
    rrc_att_sum = Column(Float)
    rrc_suces_sum = Column(Float)
