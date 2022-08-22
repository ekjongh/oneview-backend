import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class UserDashboardConfig(Base):
    __tablename__ = "USER_DASHBOARD_CONFIGS"
    modules = Column(String(2000))

    owner_id = Column(String(100), ForeignKey("users.user_id"), primary_key=True)
    owner = relationship("User", back_populates="user_dashboard_configs")
