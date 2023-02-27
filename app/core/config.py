from dataclasses import dataclass
from os import path, environ
from dotenv import load_dotenv
from typing import List

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
load_dotenv()
SQLALCHEMY_DATABASE_URL = environ.get("SQLALCHEMY_DATABASE_URL")
SQLALCHEMY_DATABASE_URL_SYNC = environ.get("SQLALCHEMY_DATABASE_URL_SYNC")

@dataclass
class Config:
    """
    기본 Configuration
    """
    BASE_DIR: str = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    DEBUG: bool = False
    TEST_MODE: bool = False
    DB_URL: str = SQLALCHEMY_DATABASE_URL
    DB_URL_SYNC: str = SQLALCHEMY_DATABASE_URL_SYNC


@dataclass
class LocalConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    DEBUG: bool = True


@dataclass
class ProdConfig(Config):
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]


@dataclass
class TestConfig(Config):
    DB_URL: str = SQLALCHEMY_DATABASE_URL
    TRUSTED_HOSTS = ["*"]
    ALLOW_SITE = ["*"]
    TEST_MODE: bool = True


def conf():
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig, local=LocalConfig, test=TestConfig)
    return config[environ.get("API_ENV", "local")]()