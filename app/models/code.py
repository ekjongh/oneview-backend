from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base

class AddrCode(Base):
    __tablename__ = "code_addr"

    sido_nm = Column(String(100), primary_key=True)
    gun_gu_nm = Column(String(100))
    eup_myun_dong_nm  = Column(String(100))


class OrgCode(Base):
    __tablename__ = "code_org"

    area_center_nm = Column(String(100), primary_key=True)
    area_team_nm = Column(String(100))
    area_jo_nm = Column(String(100))
    biz_hq_nm = Column(String(100))
    oper_team_nm = Column(String(100))
