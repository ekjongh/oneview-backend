########################################################################################################################
# 데이터베이스 세션을 생성하는 모듈(동기, 비동기)
# [ 주요 생성객체 ]
#  * SessionLocalSync : 동기 세션객체
#  * SessionLocal : 비동기 세션객체
#
# ┌-----------------┐ QUERIES   ┌-----------------┐           ┌-----------------┐
# | SESSION         |---------->| ENGINE          |---------->| CONNETION       |
# | (Sync, Async)   |<----------|                 |<-----┐    |                 |
# └-----------------┘  BIND     └-----------------┘      |    └--------┬--------┘
#                                                        |             | EXECUTE
#                                                 DB_URL |             |
#                                                        |    ┌--------∨--------┐
#                                                        └----|  DATABAS        |
#                                                             |                 |
#                                                             └-----------------┘
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.23 - 주석추가
#
########################################################################################################################
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine,AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import conf

config = conf()
SQLALCHEMY_DATABASE_URL = config.DB_URL
SQLALCHEMY_DATABASE_URL_SYNC = config.DB_URL_SYNC
# SQLALCHEMY_DATABASE_URL = 'oracle://nwai:nwai123@10.203.13.202:8316/XE'
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# cx_Oracle.makedsn("localhost", 49161, sid="xe")

engine = create_async_engine(
# engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=500
    # connect_args={"check_same_thread": False}
    # connect_args={
    #     "encoding": "UTF-8",
    #     "nencoding": "UTF-8",
    #     "mode": cx_Oracle.SYSDBA,
    #     "events": True
    # },
    # max_identifier_length=30,
)
engine_sync = create_engine(
    SQLALCHEMY_DATABASE_URL_SYNC,
    pool_recycle=500
    # connect_args={"check_same_thread": False}
    # connect_args={
    #     "encoding": "UTF-8",
    #     "nencoding": "UTF-8",
    #     "mode": cx_Oracle.SYSDBA,
    #     "events": True
    # },
    # max_identifier_length=30,
)
SessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, class_=AsyncSession, bind=engine)
# SessionLocalSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)
print("DB Connections Success!")