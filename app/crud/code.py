from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta
from app.errors import exceptions as ex


async def get_addr_code_all(db: AsyncSession, sido:str=None, gungu:str=None, dong:str=None, limit:int=100):
    # 선택 조건
    if not sido and not gungu and not dong:
        entities = [
            models.AddrCode.sido_cd.label("cd"),
            models.AddrCode.sido_nm.label("val")
        ]
        stmt = select(*entities)
        stmt = stmt.group_by(*entities)
    elif sido and not gungu and not dong:
        entities = [
            models.AddrCode.gun_gu_cd.label("cd"),
            models.AddrCode.gun_gu_nm.label("val")
        ]
        stmt = select(*entities)
        stmt = stmt.where(models.AddrCode.sido_nm == sido)
        stmt = stmt.group_by(*entities)
    elif sido and gungu and not dong:
        entities = [
            models.AddrCode.eup_myun_dong_cd.label("cd"),
            models.AddrCode.eup_myun_dong_nm.label("val")
        ]
        stmt = select(*entities)
        stmt = stmt.where(models.AddrCode.sido_nm == sido,
                          models.AddrCode.gun_gu_nm == gungu
                    )
        stmt = stmt.group_by(*entities)
    else:
        entities = [
            models.AddrCode.sido_cd.label("cd"),
            models.AddrCode.sido_nm.label("val")
        ]
        stmt = select(*entities)
        stmt = stmt.group_by(*entities)

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()


    list_code = list(map(lambda x: schemas.AddrCodeOutput(**dict(zip(query_keys, x))), query_result))
    return list_code

def get_org_code_by_team(db:Session, dept_nm:str):
    return db.query(models.OrgCode.oper_team_nm).filter(models.OrgCode.oper_team_nm==dept_nm).first()

async def get_org_code_all(db: AsyncSession):
    entities = [
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).order_by(models.OrgCode.seq_no)

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    # bonbu_set = set([r[0] for r in query_result])
    bonbu_set = list(dict.fromkeys([r[0] for r in query_result]))
    list_bonbu = []
    for bonbu in bonbu_set:
        team_set = set([r[1] for r in query_result if r[0]==bonbu])
        list_teams = []
        for  team in team_set:
            j_l = [{"id":r[2], "label":r[2]} for r in query_result if r[0] == bonbu and r[1] == team]
            # list_teams.append(schemas.OperTeamCode(oper_team_nm=team, area_jo_nms=j_l))
            list_teams.append({"id":team, "label":team, "children":j_l})

        # list_bonbu.append(schemas.OrgCodeOutput(biz_hq_nm=bonbu, oper_team_nms=list_teams))
        list_bonbu.append({"id":bonbu, "label":bonbu, "children":list_teams})

    return list_bonbu


async def get_menu_code_all(db: AsyncSession):
    entities = [
        models.MenuCode.menu1,
        models.MenuCode.menu2,
        models.MenuCode.menu3,
        models.MenuCode.menu4,
    ]
    stmt = select(*entities)

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()
    menu1_set = list(dict.fromkeys([r[0] for r in query_result]))
    list_menu = []
    for nm in menu1_set:
        list_submenu = [
            schemas.SubMenuCode(name=r[1],prods=r[2].split("|"),filters=r[3].split("|"))
            for r in query_result if r[0] == nm
        ]
        list_menu.append(schemas.MenuCodeOutput(name=nm, menus=list_submenu))

    return list_menu


# ------------------------------- Code DashBoard Config ... -------------------------------------- #
#
async def create_dashboard_config(db: Session, config_code: schemas.ConfigCode):
    """
    Dashboard Profile Create...
    권한 별 Default Dashboard profile 추가
    """
    db_board_config = models.DashboardConfigCode(auth=config_code.auth,
                                                 board_modules=config_code.board_modules)

    db.add(db_board_config)
    await db.commit()
    await db.refresh(db_board_config)
    return db_board_config


async def get_dashboard_configs(db: Session, skip: int = 0, limit: int = 100):
    entities = [
        models.DashboardConfigCode.idx,
        models.DashboardConfigCode.auth,
        models.DashboardConfigCode.board_modules,
    ]
    stmt = select(*entities).offset(skip).limit(limit)

    query = await db.execute(stmt)
    query_keys = query.keys()
    query_result = query.all()

    return list(map(lambda x: schemas.ConfigCode(**dict(zip(query_keys, x))), query_result))


#
async def get_dashboard_configs_by_auth(db: Session, auth: str):
    stmt = select(models.DashboardConfigCode.board_modules).filter(models.DashboardConfigCode.auth == auth)
    query = await db.execute(stmt)
    return query.scalar()


async def update_dashboard_config(idx:int, db: Session, board_config: schemas.ConfigCode):
    stmt = select(models.DashboardConfigCode).filter(models.DashboardConfigCode.idx == idx)
    query = await db.execute(stmt)
    db_dashboard_config = query.scalar()

    if db_dashboard_config is None:
        raise ex.NotFoundUserEx
    # dashboard_data = dashboard_schema_to_model(schema=board_config)

    config_data = board_config.dict(exclude_unset=True)
    for k, v in config_data.items():
        setattr(db_dashboard_config, k, v)
    db.add(db_dashboard_config)
    await db.commit()
    await db.refresh(db_dashboard_config)

    return db_dashboard_config


#
async def delete_dashboard_config(db: Session, idx: int):
    stmt = select(models.DashboardConfigCode).filter(models.DashboardConfigCode.idx == idx)
    query = await db.execute(stmt)
    db_dashboard_config = query.scalar()

    if db_dashboard_config is None:
        raise ex.NotFoundUserEx

    await db.delete(db_dashboard_config)
    await db.commit()
    return db_dashboard_config
