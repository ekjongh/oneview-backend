from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


# class VolteCdr(KBase):
#     __tablename__ = "dashboard_lte_vc_dd"
#
#     base_date = Column(String(8), primary_key = True)
#     sbt_bts_cd = Column(String(2000), primary_key=True)
#     cut_cacnt = Column(Integer())
#     try_cacnt = Column(Integer())
#     cmplt_cacnt = Column(Integer())
#     imcmplt_cacnt = Column(Integer())
    