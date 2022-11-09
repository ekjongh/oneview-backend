from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class AddrCode(Base):
    __tablename__ = "CODE_ADDR"

    sido_nm = Column(String(100))
    sido_cd = Column(String(100))
    gun_gu_nm = Column(String(100))
    gun_gu_cd = Column(String(100))
    eup_myun_dong_nm  = Column(String(100))
    eup_myun_dong_cd  = Column(String(100), primary_key=True)


class OrgCode(Base):
    __tablename__ = "CODE_ORG"
    seq_no = Column(Integer)
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
    area_center_nm = Column(String(100), primary_key=True)
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))


class MenuCode(Base):
    __tablename__ = "CODE_MENU"

    menu1 = Column(String(100), primary_key=True)
    menu2 = Column(String(100))
    menu3 = Column(String(200))
    menu4 = Column(String(200))


class DashboardConfigCode(Base):
    __tablename__ = "CODE_CONFIG"

    idx = Column(Integer, primary_key=True)
    auth = Column(String(100))
    board_modules = Column(String(5000))


class OrgGroup(Base):
    __tablename__ = "ORG_GROUP_TMP"

    EX_ORG_CD = Column(String(20), primary_key=True)
    NAME = Column(String(100))
    EX_COMPANY_CD = Column(String(4))
    EX_COMPANY_NM = Column(String(40))
    STATUS = Column(String(1))
    PARENT_ID = Column(String(20))
    EX_DEPT_CAP_NUM = Column(String(10))
    EX_ORG_LEVEL = Column(String(10))
    EX_ORG_ORDER = Column(String(10))


class OrgUser(Base):
    __tablename__ = "ORG_USER_TMP"

    LOGIN_ID = Column(String(10), primary_key=True)
    NAME = Column(String(128))
    STATUS = Column(String(1))
    EX_LEVEL_CD = Column(String(3))
    EX_LEVEL_NM = Column(String(40))
    EX_TITLE_CD = Column(String(3))
    EX_TITLE_NM = Column(String(40))
    EX_DEPT_CD = Column(String(20))
    EX_DEPT_NM = Column(String(100))
    EX_BONBU_CD = Column(String(6))
    EX_BONBU_NM = Column(String(100))
    EX_AGENCY_CD = Column(String(10))
    EX_AGENCY_NM = Column(String(100))
    EX_COMPANY_CD = Column(String(10))
    EX_COMPANY_NM = Column(String(40))
    EX_POSITION_CD = Column(String(50))
    EX_POSITION_NM = Column(String(255))
    EX_MANAGER_NO = Column(String(10))
    EMAIL = Column(String(50))
    MOBILE = Column(String(30))



