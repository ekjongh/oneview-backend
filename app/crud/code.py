########################################################################################################################
# 공통부문 관련 함수들을 정의한 모듈
# [ 주요 함수 리스트 ]
#  *
#  *
#  * 서비스 리스트 조회(데이터 갱신)
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.16 - 주석추가
#            - 데이터가 갱신된 테이블과 관련된 서비스들을 조회하는 함수 추가(프론트엔드 화면 자동갱신시 사용)
# 2023.02.17 - 서비스 URL : 업데이트일시를 키:값(Key : Value) 형태로 전달해 달라고 해서 수정함
#
########################################################################################################################
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal, or_
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


def get_org_code_lvl(db:Session, user:models.User):
    # lvl : jo=0, team=1, center=2, bonbu=3, all=4
    model_list = [models.OrgCode.area_jo_nm, models.OrgCode.oper_team_nm,
                  models.OrgCode.biz_hq_nm, models.OrgCode.bonbu_nm]
    group_list = [user.group_4, user.group_3, user.group_2, user.group_1]
    for idx, item in enumerate(group_list):
        result = db.query(func.count(models.OrgCode.area_jo_nm)).filter(
                    model_list[idx]==item).filter(models.OrgCode.eng_sosok == True).scalar()
        if result>0 and item:
            return idx
    return 4


def get_sub_orgs(db:Session, dept_nm:str ):
    result = []
    if dept_nm.endswith("본부"):
        result = db.query(models.OrgCode.biz_hq_nm).distinct().\
            filter(models.OrgCode.bonbu_nm == dept_nm).filter(models.OrgCode.eng_sosok == True).all()
    elif dept_nm.endswith("팀") or dept_nm.endswith("부"):
        result = db.query(models.OrgCode.area_jo_nm).distinct()\
            .filter(models.OrgCode.oper_team_nm==dept_nm).filter(models.OrgCode.eng_sosok == True).all()
    elif dept_nm.endswith("센터"):
        result = db.query(models.OrgCode.oper_team_nm).distinct()\
            .filter(models.OrgCode.biz_hq_nm==dept_nm).filter(models.OrgCode.eng_sosok == True).all()
    else:
        result = db.query(models.OrgCode.bonbu_nm).distinct()\
            .filter(models.OrgCode.eng_sosok == True).all()

    str = [r[0] for r in result]

    # if str:
    #     return '|'.join(str)
    if not str:
        return []
    return str



def get_sub_org_ord(db:Session, dept_nm:str ):
    # 부서 순서 구하기
    # select dept_nm from DASHBOARD_CONFIG
    result = []

    if dept_nm.endswith("팀") or dept_nm.endswith("부"):
        # result = db.query(models.OrgCode.area_jo_nm).distinct().filter(models.OrgCode.oper_team_nm==dept_nm).all()
        sub_stmt = select(models.OrgCode.biz_hq_nm).filter(models.OrgCode.oper_team_nm == dept_nm)
        stmt = select(models.OrgCode.oper_team_nm.label("dept")).distinct().\
            filter(models.OrgCode.biz_hq_nm.in_(sub_stmt)).filter(models.OrgCode.eng_sosok == True)
    elif dept_nm.endswith("센터"):
        sub_stmt = select(models.OrgCode.bonbu_nm).filter(models.OrgCode.biz_hq_nm == dept_nm)
        stmt = select(models.OrgCode.biz_hq_nm.label("dept")).distinct().\
            filter(models.OrgCode.bonbu_nm.in_(sub_stmt)).filter(models.OrgCode.eng_sosok == True)
    elif dept_nm.endswith("본부"):
        stmt = select(models.OrgCode.biz_hq_nm.label("dept")).distinct()

    result = db.execute(stmt).all()
    for idx, r in enumerate(result):
        if dept_nm == r[0]:
            return idx
    return 0


async def get_org_code_all(db: AsyncSession):
    entities = [
        models.OrgCode.bonbu_nm,
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).filter(models.OrgCode.eng_sosok == True).order_by(models.OrgCode.seq_no)

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
        data_item = dict(id=org_data[no], label=org_data[no], children=[])
        data_list.append(data_item)

    data_item["children"]=make_org_dict(org_data, no+1, data_item["children"]) if len(org_data) > no+1 else []

    return data_list

async def get_org_code_center(db: AsyncSession):
    entities = [
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
        models.OrgCode.area_jo_nm,
    ]
    stmt = select(*entities).filter(models.OrgCode.eng_sosok == True).order_by(models.OrgCode.seq_no)

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
                list_teams.append({"id":team, "label":team, "children": []})

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

# ======================================================================================================================
# 데이터가 갱신된 테이블에 관련된 서비스들을 조회하는 함수
# ┌--------------------------┐                                                  ┌-------------------------------┐
# | async def get_svcs_lis() |                                                  | 테이블 드랍 후 삽입하는 경우  |
# |                          |                                                  | 테이블들                      |
# └------------∧-------------┘                                                  | SUM_5G_OFF_LOAD_RATE          |
#              |                                                                | SUM_5G_OFF_LOAD_RATE_BTS,...  |
#              |                                                                └---------------┬---------------┘
#              |                                                                                |
# ┌------------┴------------------┐  SELECT ┌-----------------------┐  INSERT   ┌---------------∨---------------┐
# | db.execute                    |<----┬---| UPDATED_TABLES        |<--┬-------┤ information_schema.tables     |
# | call usp_get_updated_tables() |     |   | (temporary table)     |   |       | (system table)                |
# └-------------------------------┘     |   └-----------------------┘   |       └-------------------------------┘
#                                       |   (inner join)                |       기준일자 타임스템프 확인
#                                       |   ┌-----------------------┐   |       ┌-------------------------------┐
#                                       └---┤ CODE_SVCS_MAP         |   └-------┤ 데이터 삭제후 삽입하는 경우   |
#                                           | (table)               |           | 테이블들                      |
#                                           └-----------------------┘           | SUM_5G_OFF_LOAD_RATE_MM       |
#                                                                               | SUM_LTE_PRBUSAGE_MM           |
#                                                                               | ....                          |
#                                                                               └-------------------------------┘
# ----------------------------------------------------------------------------------------------------------------------
# 2023.02.16 - 초기모듈 작성
# ======================================================================================================================
async def get_svcs_list(db: AsyncSession, base_date: str):
    """ 데이터가 갱신된 테이블에 관련된 서비스들을 조회하는 함수
        [ 파라미터 ]
         - 기준일자 : 문자열 (예: 20230209)
        [ 반환값 ]
         - 서비스리스트 : JSON 형태 리스트
            [ { "svc_name": "/api/v1/voc/worst/",
                 "updated_date": "2023-02-09T17:20:45",
                 "tbl_name": "SUM_VOC_TXN"
              },
              ....
            ]
    """
    # 데이터베이스 프로시저를 호출한다.
    query = await db.execute(f"call usp_get_updated_tables('{base_date}')")
    query_result = query.all()

    # 쿼리 결과값을 JSON형태의 리스트로 변환한다.
    # svcs_list = [{"svc_name": svc.SVC_NAME, "updated_date": svc.UPDATED_DT, "tbl_name": svc.TBL_NAME} for svc in query_result]

    # 쿼리 결과값으로부터 컬럼명을 가져오고, 이때 컬럼명을 소문자로 변환한다.
    col_names = [desc.lower() for desc in query.keys()]

    # 쿼리 결과값을 JSON형태의 리스트로 작성한다.
    svcs_list = {}
    for row in query_result:
        # json_dict = {}
        # for i in range(len(col_names)):
        #     json_dict[col_names[i]] = row[i]
        # svcs_list.append(json_dict)

        # 서비스 URL : 업데이트일시를 키:값(Key : Value) 형태로 전달해 달라고 해서 수정함
        svcs_list[row[0]] = row[1]

    return svcs_list


