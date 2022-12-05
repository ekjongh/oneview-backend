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


def make_dashboard_config_group(db:Session, lvl:str, user: models.User):
    def get_group2(item):
        if item.catScope == "조별" and orgs[0]:
            item.group = orgs[0]
        elif item.catScope == "팀별" and orgs[1]:
            item.group = orgs[1]
        elif item.catScope == "센터별" and orgs[2]:
            item.group = orgs[2]
        return item
    def get_group(item):
        if item.catScope == "조별" and orgs[0]:
            item.group = orgs[0]
        elif item.catScope == "팀별" and orgs[1]:
            item.group = orgs[1]
        elif item.catScope == "센터별" and orgs[2]:
            # 본부 뷰의 경우 KPI가 각센터별로 표시되어야 함
            grp_list = item.group.split("|")

            if len(grp_list) == 1:
                # 샘플config의 센터명순서 조회 -> sub_org에서 해당 순서조직 return
                    ordno= get_sub_org_ord(db, item.group)
                    suborg_list = orgs[2].split("|")
                    if len(suborg_list) > ordno :
                        item.group = suborg_list[ordno]
            else:
                item.group = orgs[2]

        return item

    board_module = db.query(models.DashboardConfig.board_module).filter(models.DashboardConfig.board_id == lvl).first()

    if not board_module:
        return None

    # 저장된 부서명을 대체할 user기준 부서명
    orgs = [None for i in range(5)]
    if lvl==0: #조
        orgs[0] = user.group_4
        orgs[1] = user.group_3
        orgs[2] = user.group_2
        orgs[3] = user.group_1
    elif lvl==1: #팀프로파일은 팀과 조(하위조들) 변경
       orgs[0] = get_sub_orgs(db, dept_nm=user.group_3)
       orgs[1] = user.group_3
       orgs[2] = user.group_2
       orgs[3] = user.group_1
    elif lvl == 2: #센터프로파일은 센터와 팀(하위팀들) 변경
       orgs[1] = get_sub_orgs(db, dept_nm=user.group_2)
       orgs[2] = user.group_2
       orgs[3] = user.group_1
    elif lvl == 3: #본부프로파일은 본부와 센터 변경
       orgs[2] = get_sub_orgs(db, dept_nm=user.group_1)
       orgs[3] = user.group_1

    board_module = boardconfig_model_to_schema(board_module[0])

    board_module.banners = list(map(get_group, board_module.banners))
    board_module.cards = list(map(get_group, board_module.cards))

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
