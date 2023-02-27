from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.db.base_class import KBase


class DataCnt(KBase):
    __tablename__ = "SUM_DAT_CNT"

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
    eup_myun_dong_nm = Column(String(100))
    anals_3_prod_level_nm = Column(String(100), primary_key=True)
    g3d_upld_data_qnt = Column(Integer)
    ld_downl_data_qnt = Column(Integer)
    g3d_downl_data_qnt = Column(Integer)
    g5d_upld_data_qnt = Column(Integer)
    sru_usagecountdl = Column(Integer)
    g5d_downl_data_qnt = Column(Integer)
    ld_upld_data_qnt = Column(Integer)
    sru_usagecountul = Column(Integer)

    new_hq_nm = Column(String(50))
    new_center_nm = Column(String(50))