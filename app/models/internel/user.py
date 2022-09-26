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

    group_1 = Column(String(1000), default="네트워크부문")
    group_2 = Column(String(100), default="네트워크운용혁신담당")
    group_3 = Column(String(100), default="네트워크운용혁신담당")
    group_4 = Column(String(100), default="네트워크AI개발P-TF")
    group_5 = Column(String(100), default="네트워크AI개발P-TF")
    group_6 = Column(String(100), default="네트워크AI개발P-TF")

    board_modules = Column(String(2000), default="")

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # events_bts_comment = relationship("EventsBtsComment", back_populates="owner")