from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase



class VolteFailOrg(KBase):
    __tablename__ = "VOLTE_FAIL_ORG"

    base_date = Column(String(100), primary_key=True)
    mkng_cmpn_nm = Column(String(100))
    area_jo_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    anals_3_prod_level_nm = Column(String(100))
    try_cacnt = Column(Integer)
    comp_cacnt = Column(Integer)
    fail_cacnt = Column(Integer)
    fc373_cnt = Column(Integer)
    fc374_cnt = Column(Integer)
    fc9563_cnt = Column(Integer)
    fc8501_cnt = Column(Integer)
    fc417_cnt = Column(Integer)
    fc8210_cnt = Column(Integer)

class VolteFailBts(KBase):
    __tablename__ = "VOLTE_FAIL_BTS"

    base_ym = Column(String(100))
    year_base_week_nm = Column(String(100))
    base_date = Column(String(100), primary_key=True)
    dow_nm = Column(String(100))
    wday_eweek_div_nm = Column(String(100))
    mkng_cmpn_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    sido_nm = Column(String(100))
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm = Column(String(100))
    area_hq_nm = Column(String(100))
    area_center_nm = Column(String(100))
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))
    equip_cd = Column(String(100), primary_key=True)
    equip_nm = Column(String(100))
    anals_3_prod_level_nm = Column(String(100))
    try_cacnt = Column(Integer)
    comp_cacnt = Column(Integer)
    fail_cacnt = Column(Integer)
    fc373_cnt = Column(Integer)
    fc374_cnt = Column(Integer)
    fc9563_cnt = Column(Integer)
    fc8501_cnt = Column(Integer)
    fc417_cnt = Column(Integer)
    fc8210_cnt = Column(Integer)

class VolteFailHndset(KBase):
    __tablename__ = "VOLTE_FAIL_HNDSET"

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
    anals_3_prod_level_nm = Column(String(100), primary_key=True)
    hndset_pet_nm = Column(String(100), primary_key=True)
    sa_5g_suprt_div_nm = Column(String(100))
    try_cacnt = Column(Integer)
    comp_cacnt = Column(Integer)
    fail_cacnt = Column(Integer)
    fc373_cnt = Column(Integer)
    fc374_cnt = Column(Integer)
    fc9563_cnt = Column(Integer)
    fc8501_cnt = Column(Integer)
    fc417_cnt = Column(Integer)
    fc8210_cnt = Column(Integer)

