from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Subscr(KBase):
    __tablename__ = "sbstr"

    base_ym = Column(String(100))
    year_base_week_nm = Column(String(100))
    base_date = Column(String(100), primary_key=True)
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    sido_nm = Column(String(100), primary_key=True)
    gun_gu_nm = Column(String(100), primary_key=True)
    anals_3_prod_level_nm = Column(String(100), primary_key=True)
    hndset_pet_nm = Column(String(100), primary_key=True)
    sa_5g_suprt_div_nm = Column(String(100))
    bprod_maint_sbscr_cascnt = Column(Integer)
