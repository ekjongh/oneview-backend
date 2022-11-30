from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class DashboardConfig(Base):
    __tablename__ = "DASHBOARD_CONFIG"

    board_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    board_module = Column(String(5000))
    update_yn = Column(Boolean, default=True)
    login_config = Column(Boolean, default=False)
    owner_id = Column(String(100), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="dashboardconfig")