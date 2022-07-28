from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


class Offloading(KBase):
    __tablename__ = "dashboard_5g_off"

    base_date = Column(String(100), primary_key=True)
    year_base_week_nm = Column(String(100))
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    bts_oper_team_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100), primary_key=True)
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
    sbscr_num = Column(Integer)
    g3d_upld_data_qnt = Column(Integer)
    ld_downl_data_qnt = Column(Integer)
    g3d_downl_data_qnt = Column(Integer)
    g5d_upld_data_qnt = Column(Integer)
    sru_usagecountdl = Column(Integer)
    g5d_downl_data_qnt = Column(Integer)
    ld_upld_data_qnt = Column(Integer)
    sru_usagecountul = Column(Integer)
    g5_total_data_qnt = Column(Integer)
    g3_total_data_qnt = Column(Integer)
    gl_total_data_qnt = Column(Integer)
    sru_total_data_qnt = Column(Integer)
    total_data_qnt = Column(Integer)