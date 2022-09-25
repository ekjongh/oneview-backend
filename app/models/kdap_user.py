from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

from ..db.base_class import Base


class KdapUser(Base):
    __tablename__ = "kdap_users"

    user_id = Column(String(100), primary_key=True, index=False)
    user_name = Column(String(100), default="")
    email = Column(String(100), default="")
    phone = Column(String(100), default="")

    belong_1 = Column(String(100), default="네트워크부문")
    belong_2 = Column(String(100), default="네트워크운용혁신담당")
    belong_3 = Column(String(100), default="네트워크운용혁신담당")
    belong_4 = Column(String(100), default="네트워크AI개발P-TF")

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # items = relationship("Item", back_populates="owner")
    # blacklists = relationship("Blacklist", back_populates="owner")
    # events_bts_comment = relationship("EventsBtsComment", back_populates="owner")
    user_dashboard_configs = relationship("UserDashboardConfig", back_populates="owner")