from datetime import datetime, timedelta
from typing import Any, Union
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
load_dotenv()
# from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
JWT_SECRET_CODE = os.environ.get("JWT_SECRET_CODE")

# def create_access_token(
#     subject: Union[str, Any], expires_delta: timedelta = None
# ) -> str:
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(
#             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#         )
#     to_encode = {"exp": expire, "sub": str(subject)}
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)