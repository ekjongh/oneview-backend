from this import d
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import KBase


# class Voc(KBase):
#     __tablename__ = "dashboard_freq_voc_tb_dd"
#
#     base_ym = Column(String(2000))
#     voc_wjt_qrtc_nm = Column(String(2000))
#     equip_cd = Column(String(2000))
#     sr_tt_rcp_no = Column(String(2000))
#     sbt_bts_cd = Column(String(2000), primary_key=True)
#     base_date = Column(String(2000))

    # bts_info = relationship('Bts', foreign_keys=[sbt_bts_cd], back_populates= d, primaryjoin='Bts.sbt_bts_cd == Voc.sbt_bts_cd')