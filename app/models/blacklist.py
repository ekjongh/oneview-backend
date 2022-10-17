from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base

class Blacklist(Base):
    __tablename__ = "blacklists"

    id = Column(String(100), primary_key=True)
    token = Column(String(100))
    owner_id = Column(String(100), ForeignKey("USERS.user_id"))
    owner = relationship("User", back_populates="blacklists")