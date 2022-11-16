from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal, or_, and_

from app.errors import exceptions as ex
from app.crud.code import get_org_code_by_team
from .. import models, schemas
from app.utils.internel.user import user_model_to_schema, user_schema_to_model
import json


def db_insert_dashboard_config_by_id(db: Session, user_id: str, board_config: schemas.DashboardConfigIn):
    """
    Dashboard Profile Create...
    권한 별 Default Dashboard profile 설정 추가작업 필요...
    """
    db_board_config = models.DashboardConfig(owner_id=user_id)

    board_config_data = board_config.dict(exclude_unset=True)

    for k, v in board_config_data.items():
        setattr(db_board_config, k, v)

    db.add(db_board_config)
    db.commit()
    db.refresh(db_board_config)
    return db_board_config


def db_get_dashboard_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DashboardConfig).offset(skip).limit(limit).all()


def db_get_dashboard_configs_by_userid(db: Session, user_id: str):
    entities = [
        models.DashboardConfig.board_id,
        models.DashboardConfig.name,
        models.DashboardConfig.update_yn,
        models.DashboardConfig.owner_id,
    ]
    stmt = select(*entities).filter(or_(models.DashboardConfig.owner_id == user_id, models.DashboardConfig.owner_id == "admin"))
    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    if not query_result:
        return []
    else:
        return list(map(lambda x: schemas.DashboardConfigList(**dict(zip(query_keys, x))), query_result))


def db_get_dashboard_config_by_id(db: Session, board_id: int):
    entities = [
        models.DashboardConfig.board_id,
        models.DashboardConfig.name,
        models.DashboardConfig.update_yn,
        models.DashboardConfig.owner_id,
        models.DashboardConfig.board_module,
    ]
    stmt = select(*entities).filter(models.DashboardConfig.board_id == board_id)
    return db.execute(stmt).first()


def db_update_dashboard_config_by_id(board_id:int, db: Session, board_config: schemas.DashboardConfigIn):
    db_dashboard_config = db.query(models.DashboardConfig).filter(models.DashboardConfig.board_id == board_id).first()
    if db_dashboard_config is None:
        raise ex.NotFoundUserEx
    # dashboard_data = dashboard_schema_to_model(schema=board_config)
    board_config_data = board_config.dict(exclude_unset=True)

    for k, v in board_config_data.items():
        setattr(db_dashboard_config, k, v)

    db.add(db_dashboard_config)
    db.commit()
    db.refresh(db_dashboard_config)

    return db_dashboard_config


def db_delete_dashboard_config_by_id(db: Session, board_id: int):
    db_board_config = db.query(models.DashboardConfig).filter(models.DashboardConfig.board_id == board_id).first()

    if db_board_config is None:
        raise ex.APIException

    db.delete(db_board_config)
    db.commit()
    return db_board_config

def db_count_dashboard_config_by_id(db: Session, user_id: str):
    stmt = select(func.count(models.DashboardConfig.board_id)).filter(models.DashboardConfig.owner_id == user_id)
    return db.execute(stmt).scalar()


def db_insert_dashboard_config_by_default(db: Session, user: models.User ):
    if get_org_code_by_team(db=db, dept_nm=user.group_3):
        #엔지부 소속
        stmt = select(models.DashboardConfig.board_module).\
            filter(and_(models.DashboardConfig.owner_id == "admin",models.DashboardConfig.name == "default_직원"))
        print("DEFAULTCONFIG 직원용")
        board_config = db.execute(stmt).scalar().format(c_txt="팀별",g_txt=user.group_3)
    else:
        #staff
        stmt = select(models.DashboardConfig.board_module).\
            filter(and_(models.DashboardConfig.owner_id == "admin",models.DashboardConfig.name == "default_staff"))
        print("DEFAULTCONFIG STAFF")
        board_config = db.execute(stmt).scalar().format(c_txt="팀별",g_txt=user.group_3)

    db_board_config = models.DashboardConfig(owner_id=user.user_id,
                                             name="default_config",
                                             board_module=board_config)

    db.add(db_board_config)
    db.commit()
    db.refresh(db_board_config)
    return db_board_config