from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..db.base_class import Base


class EventsBtsComment(Base):
    __tablename__ = "events_bts_comment"

    id = Column(String(100), primary_key=True)
    comment = Column(String(20))

    owner_bts_id = Column(String(100), ForeignKey("events_bts.id"))
    bts = relationship("EventsBts", back_populates="events_bts_comment")
    owner_user_id = Column(String(100), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="events_bts_comment")
