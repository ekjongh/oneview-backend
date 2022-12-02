from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True, index=False)
    user_name = Column(String(100), default="")
    email = Column(String(100), default="")
    phone = Column(String(100), default="")

    group_1 = Column(String(1000), default="")
    group_2 = Column(String(100), default="")
    group_3 = Column(String(100), default="")
    group_4 = Column(String(100), default="")

    # board_modules = Column(String(4000), default="")

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    level = Column(String(50), default="")
    auth = Column(String(30), default="직원") #직원, 팀장, 광역본부장/센터장, 부문장/스텝본부장
    board_id = Column(Integer) # 동기화 board id
    start_board_id = Column(Integer) # 로그인시 사용할 config id

    blacklists = relationship("Blacklist", back_populates="owner")
    dashboardconfig = relationship("DashboardConfig", back_populates="owner")
    # events_bts_comment = relationship("EventsBtsComment", back_populates="owner")