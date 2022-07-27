from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base_class import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(String(100), primary_key=True)
    title = Column(String(20))
    description = Column(String(20))
    owner_id = Column(String(100), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="items")
