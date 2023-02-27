from datetime import datetime
import re

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr, declarative_base


@as_declarative()
class Base:
    # id = Column(Integer, primary_key=True, index=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    __name__: str

    # CamelCase의 클래스 이름으로부터 snake_case의 테이블 네임 자동 생성
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).upper()


KBase = declarative_base()
