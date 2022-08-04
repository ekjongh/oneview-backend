from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base


class EventsBts(Base):
    __tablename__ = "events_bts"
    id = Column(String(100), primary_key=True)
    sbt_bts_cd = Column(String(100))
    event_type = Column(String(100))
    event_type_detail = Column(String(100))

    events_bts_comment = relationship("EventsBtsComment", back_populates="bts")