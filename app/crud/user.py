from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.security import get_password_hash
from app.utils.internel.user import dashboard_schema_to_model


def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)

    db_user = models.User(user_id=user.user_id,
                          hashed_password=hashed_password)
    db_board_config = models.UserDashboardConfig(owner_id=user.user_id)
    db.add(db_user)
    db.add(db_board_config)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_superuser(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(user_id=user.user_id,
                          # username=user.username,
                          # email=user.email,
                          # phone=user.phone,
                          hashed_password=hashed_password,
                          is_active=True,
                          is_superuser=True)
    db_board_config = models.UserDashboardConfig(owner_id=user.user_id)
    db.add(db_user)
    db.add(db_board_config)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, user: schemas.UserOutput):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)
    for k, v in user_data.items():
        setattr(db_user, k, v)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user


# ------------------------------- User DashBoard Config ... -------------------------------------- #

def create_dashboard_config(db: Session, board_config: schemas.UserBoardConfigBase):
    # id = board_config.owner_id + "_" + board_config.config_nm
    db_board_config = models.UserDashboardConfig(**board_config.__dict__, id=id)

    db.add(db_board_config)
    db.commit()
    db.refresh(db_board_config)
    return db_board_config


def get_dashboard_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserDashboardConfig).offset(skip).limit(limit).all()


def get_dashboard_configs_by_id(db: Session, user_id: str):
    return db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == user_id).all()


# def get_dashboard_config_by_id(db: Session, id: str):
#     return db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.id == id).first()


def update_dashboard_config(id:str, db: Session, board_config: schemas.UserBoardConfig):
    db_dashboard_config = db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == id).first()
    if db_dashboard_config is None:
        raise HTTPException(status_code=404, detail="UserDashboardConfig not found")
    db_dashboard_config = dashboard_schema_to_model(update_model=db_dashboard_config, schema=board_config)
    
    db.add(db_dashboard_config)
    db.commit()
    db.refresh(db_dashboard_config)
    return db_dashboard_config


def delete_dashboard_config(db: Session, id: str):
    # id = board_config.owner_id + "_" + board_config.config_nm
    db_board_config = db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.id == id).first()

    if db_board_config is None:
        raise HTTPException(status_code=404, detail="User Dashboard Config not found")

    db.delete(db_board_config)
    db.commit()
    return db_board_config



