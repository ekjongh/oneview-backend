from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Volte(KBase):
    __tablename__ = "dashboard_volte_dd"

    base_ym = Column(String(2000))
    base_date = Column(String(2000), primary_key=True)
    equip_cd = Column(String(2000), primary_key=True)
    equip_nm = Column(String(2000))
    bts_biz_hq_cd = Column(String(2000))
    bts_biz_hq_nm = Column(String(2000))
    oper_team_nm = Column(String(2000))
    area_hq_nm = Column(String(2000))
    area_center_nm = Column(String(2000))
    area_jo_nm = Column(String(2000))
    area_team_nm = Column(String(2000))
    wjxbfs1 = Column(Integer)
    wjxbfs2 = Column(Integer)
    wjxbfs3 = Column(Integer)
    wjxbfs4 = Column(Integer)
    sido_nm = Column(String(2000))
    eup_myun_dong_nm = Column(String(2000))
    gun_gu_nm = Column(String(2000))
    bj_nm = Column(String(2000))

class VolteFc(KBase):
    __tablename__ = "dashboard_volte_fc"

    base_date = Column(String(2000), primary_key=True)
    area_hq_nm = Column(String(2000))
    area_center_nm = Column(String(2000))
    area_jo_nm = Column(String(2000))
    area_team_nm = Column(String(2000), primary_key=True)
    adm_dong = Column(String(2000), primary_key=True)
    oper_team_nm = Column(String(2000))
    fc = Column(String(2000), primary_key=True)
    wjxbfs1 = Column(Integer)