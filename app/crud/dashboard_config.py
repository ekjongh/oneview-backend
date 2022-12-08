from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal, or_, and_

from app.errors import exceptions as ex
from app.crud.code import get_org_code_by_team, get_org_code_lvl, get_sub_orgs, get_sub_org_ord
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
        models.DashboardConfig.login_config,
    ]
    stmt = select(*entities).filter(models.DashboardConfig.owner_id == user_id)
    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    if not query_result:
        return []
    return list(map(lambda x: schemas.DashboardConfigList(**dict(zip(query_keys, x))), query_result))


def db_get_dashboard_default_configs_by_user(db:Session, user:models.User):
    # default config 중에 조회가능한 목록
    lvl = get_org_code_lvl(db, user)

    entities = [
        models.DashboardConfig.board_id,
        models.DashboardConfig.name,
        models.DashboardConfig.update_yn,
        models.DashboardConfig.owner_id,
        models.DashboardConfig.login_config,
    ]
    # stmt = select(*entities).filter(and_(models.DashboardConfig.owner_id == "admin",
    #                                      models.DashboardConfig.board_id>=lvl,
    #                                      models.DashboardConfig.board_id<=10))
    stmt = select(*entities).filter(models.DashboardConfig.owner_id == "admin")

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

    boardconfig = schemas.DashboardConfigOut(**result.__dict__)
    # boardconfig = schemas.DashboardConfigOut(result)
    return boardconfig


def db_get_dashboard_config_by_name(db: Session, board_name: str):
    result = db.query(models.DashboardConfig).filter(models.DashboardConfig.name == board_name).first()
    if not result:
        return None

    boardconfig = schemas.DashboardConfigOut(**result.__dict__)

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
    # user조직으로 가능한 샘플 config 목록 중 0번째 선택
    lvl = get_org_code_lvl(db, user)

    board_module = make_dashboard_config_group(db, lvl, user)

    db_board_config = models.DashboardConfig(owner_id=user.user_id,
                                             name="workingProfile",
                                             board_module=board_module)
    db.add(db_board_config)
    db.commit()
    db.refresh(db_board_config)
    return db_board_config

def get_group(group:str, lst:[], val:str):
    # 배너,카드의 그룹명 변경: all-> list, 0~4-> list[0~4], !-> user.group_1~4
    if group == "all":
        group = "|".join(lst)
    elif group == "!" and val:
        group = val
    elif group.isdigit():
        if int(group) < len(lst):
            group = lst[int(group)]
        else:
            group = None
    return group

def get_item(item, orgs):
    # 배너,카드의 그룹명 변경: all-> list, 0~4-> list[0~4], str-> user.group_1~4
    if item.catScope == "조별":
        item.group = get_group(item.group, orgs["jo_list"], orgs["jo"])
    elif item.catScope == "팀별":
        item.group = get_group(item.group, orgs["team_list"], orgs["team"])
    elif item.catScope == "센터별":
        item.group = get_group(item.group, orgs["center_list"], orgs["center"])
    elif item.catScope == "본부별":
        item.group = get_group(item.group, orgs["bonbu_list"], orgs["bonbu"])

    return item


def make_dashboard_config_group(db:Session, lvl:str, user: models.User):
    board_module = db.query(models.DashboardConfig.board_module).filter(models.DashboardConfig.board_id == lvl).first()

    if not board_module:
        return None

    # 저장된 부서명을 대체할 user기준 부서명 :
    orgs = {}
    orgs["jo"] = user.group_4
    orgs["jo_list"] = get_sub_orgs(db, dept_nm=user.group_3)
    orgs["team"] = user.group_3
    orgs["team_list"] = get_sub_orgs(db, dept_nm=user.group_2)
    orgs["center"] = user.group_2
    orgs["center_list"] = get_sub_orgs(db, dept_nm=user.group_1)
    orgs["bonbu"] = user.group_1
    orgs["bonbu_list"] = get_sub_orgs(db, dept_nm='')

    board_module = boardconfig_model_to_schema(board_module[0])

    board_module.banners = list(map(lambda p: get_item(p, orgs), board_module.banners))
    board_module.banners = [item for item in board_module.banners if item.group]
    board_module.cards = list(map(lambda p: get_item(p, orgs), board_module.cards))
    board_module.cards = [item for item in board_module.cards if item.group]

    m_board_config = boardconfig_schema_to_model(board_module)

    return m_board_config



def db_get_dashboard_default_config_by_id(db: Session, board_id: int, client:models.User):
    result = db.query(models.DashboardConfig).filter(models.DashboardConfig.board_id == board_id).first()
    if not result:
        return None

    boardconfig = schemas.DashboardConfigOut(**result.__dict__)

    if boardconfig.owner_id != "admin" and client.user_id != boardconfig.owner_id:
        return {"result":None}
    if boardconfig.owner_id == "admin" and client.user_id != boardconfig.owner_id:
        boardconfig.board_module = make_dashboard_config_group(db, lvl=board_id, user=client)

    return boardconfig
