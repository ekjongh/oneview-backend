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
        models.OrgCode.bonbu_nm,
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).order_by(models.OrgCode.seq_no)

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    list_bonbu = []
    for x in query_result:
        list_bonbu = make_org_dict(x, 0, list_bonbu)

    return list_bonbu

def make_org_dict(org_data:[], no:int, data_list:[]):
    fl = list(filter(lambda x:x["id"]==org_data[no], data_list))
    if len(fl) > 0:
        data_item = fl[0]
    else :
        data_item = dict(id=org_data[no], label=org_data[no], child=[])
        data_list.append(data_item)

    data_item["child"]=make_org_dict(org_data, no+1, data_item["child"]) if len(org_data) > no+1 else None

    return data_list

async def get_org_code_center(db: AsyncSession):
    entities = [
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).order_by(models.OrgCode.seq_no)

    query = await db.execute(stmt)
    query_result = query.all()
    query_keys = query.keys()

    center_set = list(dict.fromkeys([r[0] for r in query_result]))
    list_center = []
    for center in center_set:
        team_set = set([r[1] for r in query_result if r[0]==center])
        list_teams = []
        for team in team_set:
            j_l = [{"id":r[2], "label":r[2]} for r in query_result if r[0] == center and r[1] == team and r[2] !=""]

            if len(j_l) > 0 :
                list_teams.append({"id": team, "label": team, "children": j_l})
            else:
                list_teams.append({"id":team, "label":team, "children": None})

        list_center.append({"id":center, "label":center, "children":list_teams})

    return list_center

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

