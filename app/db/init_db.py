########################################################################################################################
# 데이터베이스 초기화 관련 모듈
# - 환경변수 파일(.env)로부터 값을 읽어 들인다.
# - 로그이력을 기록하기 위한 로거(logger)를 생성한다.
# - 관리자 계정이 없는 경우 관리자 계정을 데이터베이스에 생성한다.
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.20 - 주석추가
# 2023.02.21 - 불필요한 코드 삭제 및 주석 추가
########################################################################################################################
import os
import logging
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.crud.user import create_superuser, get_user_by_id
from app.schemas.user import UserCreate
from app.db import base  # noqa: F401

# 로그내역을 작성하기 위한 로거를 생성한다.
logger = logging.getLogger(__name__)

# 파일로부터 환경변수를 읽어온다.
load_dotenv()

# 환경변수로부터 관리자 정보를 가져온다.
FIRST_SUPERUSER_ID = os.environ.get("FIRST_SUPERUSER_ID")           # 관리자ID
FIRST_SUPERUSER_NAME = os.environ.get("FIRST_SUPERUSER_NAME")       # 관리자명
FIRST_SUPERUSER_EMAIL = os.environ.get("FIRST_SUPERUSER_EMAIL")     # 관리자 이메일
# FIRST_SUPERUSER_PW = os.environ.get("FIRST_SUPERUSER_PW")

def init_db(db: Session) -> None:
    """ 데이터베이스를 초기화 한다.
        1) 관리자 계정이 없는 경우 관리자 계정을 데이터베이스에 생성한다.
    """
    if FIRST_SUPERUSER_ID:
        superuser = get_user_by_id(db=db, user_id=FIRST_SUPERUSER_ID)  # 2
        if not superuser:
            user_in = UserCreate(
                user_id=FIRST_SUPERUSER_ID,
                username=FIRST_SUPERUSER_NAME,
                email=FIRST_SUPERUSER_EMAIL,
                # password=FIRST_SUPERUSER_PW,
                # email=FIRST_SUPERUSER_EMAIL,
                # username=FIRST_SUPERUSER_NAME,
                # is_superuser=True,
            )
            create_superuser(db, user_in)
            logger.info(
                "Creating superuser Success. User with email "
                f"{FIRST_SUPERUSER_ID} created. "
            )
        else:
            logger.warning(
                "Skipping creating superuser. User with email "
                f"{FIRST_SUPERUSER_ID} already exists. "
            )