from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal, or_, and_

from app.errors import exceptions as ex
from app.crud.code import get_org_code_by_team
from .. import models, schemas
from app.utils.internel.user import boardconfig_schema_to_model, boardconfig_model_to_schema





def db_insert_dashboard_config_by_id(db: Session, user_id: str, board_config: schemas.DashboardConfigIn):
    """
    Dashboard Profile Create...
    권한 별 Default Dashboard profile 설정 추가작업 필요...
    """
    db_board_config = models.DashboardConfig(owner_id=user_id)

    board_config_data = board_config.dict(exclude_unset=True)
    # board_config_data.board_module = boardconfig_schema_to_model(board_config_data.board_module)

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
    return list(map(lambda x: schemas.DashboardConfigList(**dict(zip(query_keys, x))), query_result))


def db_get_dashboard_config_by_id(db: Session, board_id: int):
    result = db.query(models.DashboardConfig).filter(models.DashboardConfig.board_id == board_id).first()
    if not result:
        return None

    boardconfig = schemas.DashboardConfigOut(board_id=board_id,
                                            name=result.name,
                                            owner_id=result.owner_id,
                                            update_yn=result.update_yn,
                                            board_module=result.board_module)

    return boardconfig


def db_get_dashboard_config_by_name(db: Session, board_name: str):
    result = db.query(models.DashboardConfig).filter(models.DashboardConfig.name == board_name).first()
    if not result:
        return None

    boardconfig = schemas.DashboardConfigOut(board_id=result.board_id,
                                             name=result.name,
                                             owner_id=result.owner_id,
                                             update_yn=result.update_yn,
                                             board_module=result.board_module)

    return boardconfig


def db_update_dashboard_config_by_id(board_id:int, db: Session, board_config: schemas.DashboardConfigIn):
    db_dashboard_config = db.query(models.DashboardConfig).filter(models.DashboardConfig.board_id == board_id).first()
    if db_dashboard_config is None:
        raise ex.NotFoundUserEx

    # board_config.board_module = boardconfig_schema_to_model(board_config.board_module)
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

def db_is_my_config_by_id(db: Session, board_id: str, user_id:str):
    stmt = select(models.User.board_id).filter(models.User.user_id==user_id)
    # stmt = select(func.count(models.DashboardConfig.board_id)).\
    #     filter(and_(models.DashboardConfig.board_id == board_id, models.DashboardConfig.name == "my_config"))
    user_board_id = db.execute(stmt).scalar()
    if user_board_id == board_id:
        return True
    else:
        return False


def db_insert_dashboard_config_by_default(db: Session, user: models.User ):
    if get_org_code_by_team(db=db, dept_nm=user.group_3):
        #엔지부 소속
        # board_config= db_get_dashboard_config_by_name(db, board_name="masterProfile4Employees")
        board_config = db.query(models.DashboardConfig).filter(models.DashboardConfig.name == "masterProfile4Employees").first()
    else:
        #staff
        # board_config= db_get_dashboard_config_by_name(db, board_name="masterProfile4Management")
        board_config = db.query(models.DashboardConfig).filter(models.DashboardConfig.name == "masterProfile4Management").first()

    if not board_config:
        return None

    board_module = change_dashboard_config_group(board_config.board_module, user)
    board_module = boardconfig_schema_to_model(board_module)
    db_board_config = models.DashboardConfig(owner_id=user.user_id,
                                             name="workingprofile",
                                             board_module=board_module)

    db.add(db_board_config)
    db.commit()
    db.refresh(db_board_config)
    return db_board_config


def change_dashboard_config_group(board_config: schemas.ModuleConfigBase, user: models.User):
    board_config = boardconfig_model_to_schema(board_config)
    def get_group(item):
        if item.catScope == "조별" and user.group_4:
            item.group = user.group_4
        elif item.catScope == "팀별" and user.group_3:
            item.group = user.group_3
        elif item.catScope == "센터별" and user.group_2:
            item.group = user.group_2
        return item

    board_config.banners = list(map(get_group, board_config.banners))
    board_config.cards = list(map(get_group, board_config.cards))

    return board_config


