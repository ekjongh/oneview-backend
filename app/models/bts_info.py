from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Bts(KBase):
    __tablename__ = "dashboard_bts_info_dd"

    equip_nm = Column(String(2000))
    cell_cd = Column(String(2000))
    oper_team_nm = Column(String(2000))
    addr_dtl = Column(String(2000))
    bld_flor = Column(String(2000))
    biz_hq_nm = Column(String(2000))
    sbt_bts_cd = Column(String(2000), primary_key=True)
    base_date = Column(String(2000))
    area_team_cd = Column(String(2000))
    area_center_cd = Column(String(2000))
    area_jo_nm = Column(String(2000))
    area_team_nm = Column(String(2000))
    area_center_nm = Column(String(2000))
    area_hq_cd = Column(String(2000))