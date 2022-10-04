from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


def get_addr_code_all(db: Session, sido:str=None, gungu:str=None, dong:str=None, limit:int=100):
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
    # print(stmt.compile(compile_kwargs={"literal_binds": True}))


    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()


    list_code = list(map(lambda x: schemas.AddrCodeOutput(**dict(zip(query_keys, x))), query_result))
    return list_code


def get_org_code_all(db: Session):
    entities = [
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).order_by(models.OrgCode.seq_no)

    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    # bonbu_set = set([r[0] for r in query_result])
    bonbu_set = list(dict.fromkeys([r[0] for r in query_result]))
    list_bonbu = []
    for bonbu in bonbu_set:
        team_set = set([r[1] for r in query_result if r[0]==bonbu])
        list_teams = []
        for  team in team_set:
            j_l = [r[2] for r in query_result if r[0] == bonbu and r[1] == team]
            list_teams.append(schemas.OperTeamCode(oper_team_nm=team, area_jo_nms=j_l))
        print(list_teams)

        list_bonbu.append(schemas.OrgCodeOutput(biz_hq_nm=bonbu, oper_team_nms=list_teams))

    return list_bonbu




def get_menu_code_all(db: Session):
    entities = [
        models.MenuCode.menu1,
        models.MenuCode.menu2,
        models.MenuCode.menu3,
        models.MenuCode.menu4,
    ]
    stmt = select(*entities)
    #print(stmt.compile(compile_kwargs={"literal_binds": True}))
    query = db.execute(stmt)
    query_result = query.fetchall()
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
