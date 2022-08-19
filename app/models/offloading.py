from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase



class Offloading_Bts(KBase):
    __tablename__ = "offloading_bts"

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
    g3d_upld_data_qnt = Column(Integer)
    ld_downl_data_qnt = Column(Integer)
    g3d_downl_data_qnt = Column(Integer)
    g5d_upld_data_qnt = Column(Integer)
    sru_usagecountdl = Column(Integer)
    g5d_downl_data_qnt = Column(Integer)
    ld_upld_data_qnt = Column(Integer)
    sru_usagecountul = Column(Integer)



class Offloading_Hndset(KBase):
    __tablename__ = "offloading_hndset"

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
    eup_myun_dong_nm = Column(String(100), primary_key=True)
    hndset_pet_nm = Column(String(100), primary_key=True)
    sa_5g_suprt_div_nm = Column(String(100))
    g3d_upld_data_qnt = Column(Integer)
    ld_downl_data_qnt = Column(Integer)
    g3d_downl_data_qnt = Column(Integer)
    g5d_upld_data_qnt = Column(Integer)
    sru_usagecountdl = Column(Integer)
    g5d_downl_data_qnt = Column(Integer)
    ld_upld_data_qnt = Column(Integer)
    sru_usagecountul = Column(Integer)

