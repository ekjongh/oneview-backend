import logging
from sqlalchemy.orm import Session
#  환경변수
import os
from dotenv import load_dotenv

from app.core.security import get_password_hash
from app.crud.user import create_superuser, get_user_by_id
from app.db.session import engine
from app.schemas.user import UserCreate
from app.db import base  # noqa: F401
from app.db.base import Base

logger = logging.getLogger(__name__)
load_dotenv()
# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

FIRST_SUPERUSER_ID = os.environ.get("FIRST_SUPERUSER_ID")
FIRST_SUPERUSER_NAME = os.environ.get("FIRST_SUPERUSER_NAME")
FIRST_SUPERUSER_EMAIL = os.environ.get("FIRST_SUPERUSER_EMAIL")
# FIRST_SUPERUSER_PW = os.environ.get("FIRST_SUPERUSER_PW")

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    Base.metadata.create_all(bind=engine)

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
        else:
            logger.warning(
                "Skipping creating superuser. User with email "
                f"{FIRST_SUPERUSER_ID} already exists. "
            )
