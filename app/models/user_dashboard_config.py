import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class UserDashboardConfig(Base):
    __tablename__ = "USER_DASHBOARD_CONFIGS"
    id = Column(String(100), primary_key=True)
    config_nm = Column(String(100))

    dashboard_kpi_1 = Column(String(100))
    dashboard_type_1 = Column(String(100))
    dashboard_group_1 = Column(String(100)) # team / jo / center
    dashboard_date_1 = Column(String(100)) # day / week / month

    dashboard_kpi_2 = Column(String(100))
    dashboard_type_2 = Column(String(100))
    dashboard_group_2 = Column(String(100))
    dashboard_date_2 = Column(String(100))
    
    dashboard_kpi_3 = Column(String(100))
    dashboard_type_3 = Column(String(100))
    dashboard_group_3 = Column(String(100))
    dashboard_date_3 = Column(String(100))
    
    dashboard_kpi_4 = Column(String(100))
    dashboard_type_4 = Column(String(100))
    dashboard_group_4 = Column(String(100))
    dashboard_date_4 = Column(String(100))
    
    dashboard_kpi_5 = Column(String(100))
    dashboard_type_5 = Column(String(100))
    dashboard_group_5 = Column(String(100))
    dashboard_date_5 = Column(String(100))
    
    dashboard_kpi_6 = Column(String(100))
    dashboard_type_6 = Column(String(100))
    dashboard_group_6 = Column(String(100))
    dashboard_date_6 = Column(String(100))

    event_kpi_1 = Column(String(100))
    event_type_1 = Column(String(100))
    event_group_1 = Column(String(100))
    event_kpi_2 = Column(String(100))
    event_type_2 = Column(String(100))
    event_group_2 = Column(String(100))
    event_kpi_3 = Column(String(100))
    event_type_3 = Column(String(100))
    event_group_3 = Column(String(100))

    owner_id = Column(String(100), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="user_dashboard_configs")
