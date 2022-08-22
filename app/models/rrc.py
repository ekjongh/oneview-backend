from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Rrc(KBase):
    __tablename__ = "rrc"

    base_ym = Column(String(100))
    year_base_week_nm = Column(String(100))
    base_date = Column(String(100), primary_key=True)
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100), primary_key=True)
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
    latit_val = Column(String(50))
    lngit_val = Column(String(50))
    prbusage = Column(Float)
    rrcattempt = Column(Integer)
    rrc_success = Column(Integer)
    rrc_success_rate = Column(Float)