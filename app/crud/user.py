from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal

from app.errors import exceptions as ex
from .. import models, schemas
from app.utils.internel.user import user_model_to_schema, user_schema_to_model
import json

# def user_model_to_schema(user):
#     user.board_modules = json.loads(user.board_modules)
#     return user
#
# def user_schema_to_model(user):
#     user.board_modules = json.dumps([dict(obj) for obj in user.board_modules])
#     return user


async def get_user_by_id(db: AsyncSession, user_id: str):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = await db.execute(stmt)
    user = query.scalar()
    # board_module 형식 []->str 변경으로 미사용
    # if user: 
    #     user = user_model_to_schema(user)
    return user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(models.User).offset(skip).limit(limit)
    query = await db.execute(stmt)
    users = query.scalars().all()
    # board_module 형식 []->str 변경으로 미사용
    # if len(users) != 0:
    #     users = list(map(user_model_to_schema, users))
    return users


async def create_user(db: Session, user: schemas.UserCreate):

    # db_user = models.User(user_id=user.user_id,
    #                       board_modules=json.dumps(list()))
    db_user = models.User(user_id=user.user_id)
    entities = [
        models.OrgUser.LOGIN_ID,
        models.OrgUser.NAME,
        models.OrgUser.EX_POSITION_NM,
        models.OrgUser.EX_LEVEL_NM,
        models.OrgUser.EMAIL,
        models.OrgUser.MOBILE,

    ]
    stmt = select(*entities).where(models.OrgUser.LOGIN_ID == user.user_id)

    query = await db.execute(stmt)
    query_result = query.first()
    print(stmt.compile(compile_kwargs={"literal_binds": True}))

    if not query_result:
        raise HTTPException(status_code=401,detail="Bad user id")
    else :
        db_user.user_name = query_result["NAME"]
        db_user.email = query_result["EMAIL"]
        db_user.phone = query_result["MOBILE"]
        db_user.level = query_result["EX_LEVEL_NM"]
        depts = query_result["EX_POSITION_NM"].split(" ")
        j=0
        for i in range(4-min(3, len(depts)), 4):
            setattr(db_user, f"group_{i}", depts[j])
            print(f"group_{i} : {depts[j]}")
            j = j+1
        # db_user["group_1"] = query_result["EX_POSITION_NM"]

        # board_modules default :  get_default_board_modules(level, group_2, group_3)
        #   팀 직원 로그인-> 직원&팀
        #   팀장 로그인 -> 팀장&팀
        #   센터장 로그인-> 센터&센터
        #   그외 -> default.(강남엔지니어링부. 전국?)
        #   조 직원 로그인(config수정한경우) -> 직원&조
        print("user select", db_user.level, db_user.group_3)
        db_user.board_modules = get_default_board_modules(db, db_user.level, db_user.group_3)
        print(db_user.board_modules)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def create_superuser(db: Session, user: schemas.UserCreate):
    db_user = models.User(user_id=user.user_id,
                          board_modules=json.dumps(list()),
                          # username=user.username,
                          # email=user.email,
                          # phone=user.phone,
                          is_active=True,
                          is_superuser=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def update_user(db: Session, user_id: str, user: schemas.UserOutput):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = await db.execute(stmt)
    db_user = query.scalar()

    if db_user is None:
        raise ex.NotFoundUserEx

    # board_module 형식 []->str 변경으로 미사용
    # user = user_schema_to_model(user)

    user_data = user.dict(exclude_unset=True)
    for k, v in user_data.items():
        setattr(db_user, k, v)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise ex.NotFoundUserEx
    db.delete(db_user)
    db.commit()
    return db_user

def get_default_board_modules(db: Session, level: str="직원", group: str="" ):
    default_config = """
             {{"banners": 
              [
                {{"catIndicator":"천명당VOC",
                 "catProductService":"5G",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"품질 VOC 발생 5G",
                 "dates":"최근갱신일"
                }}, 
                {{"catIndicator":"천명당VOC",
                 "catProductService":"LTE",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"품질 VOC 발생 LTE",
                 "dates":"최근갱신일"
                }},                 
                {{"catIndicator":"VOLTE절단율",
                 "catProductService":"5G",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"VoLTE 절단율",
                 "dates":"최근갱신일"
                }}, {{
                 "catIndicator":"오프로딩율_5G",
                 "catProductService":"5G",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"5G 오프로드율",
                 "dates":"최근갱신일"
                }},{{
                 "catIndicator":"MDT",
                 "catProductService":"_",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"MDT 불량률",
                 "dates":"최근갱신일"
                }},{{
                 "catIndicator":"LTE기지국통계RRC",
                 "catProductService":"RRC성공률",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"RRC성공률",
                 "dates":"최근갱신일"
                }}
              ], 
             "cards": 
              [
                {{"catIndicator":"천명당VOC",
                 "catPresentationFormat":"일별추이",
                 "catProductService":"5G",
                 "catScope":"{c_txt}",
                 "group":"{g_txt}",
                 "title":"품질 VOC 발생 5G",
                 "caption":"천명당VOC / 일별추이 / 5G / {c_txt} / {g_txt}",
                 "dates":"2주간"
                }}, {{
                  "catIndicator":"VOLTE절단율",
                  "catPresentationFormat":"일별추이",
                  "catProductService":"5G",
                  "catScope":"{c_txt}",
                  "group":"{g_txt}",
                  "title":"VoLTE 절단율 5G",
                  "caption":"VoLTE절단율 / 일별추이 / 5G / {c_txt} / {g_txt}",
                  "dates":"2주간"
                }}, {{
                  "catIndicator":"오프로딩율_5G",
                  "catPresentationFormat":"일별추이",
                  "catProductService":"5G",
                  "catScope":"{c_txt}",
                  "group":"{g_txt}",
                  "title":"5G 오프로드율",
                  "caption":"오프로딩율_5G / 일별추이 / 5G / {c_txt} / {g_txt}",
                  "dates":"2주간"
                }}, {{
                  "catIndicator":"단말별가입자수",
                  "catPresentationFormat":"_",
                  "catProductService":"5G",
                  "catScope":"{c_txt}",
                  "group":"{g_txt}",
                  "title":"5G 단말 기종별 고객 수 5G",
                  "caption":"단말별가입자수 / 5G / {c_txt} / {g_txt}",
                  "dates":"어제"
                }}, {{
                  "catIndicator":"MDT",
                  "catPresentationFormat":"일별추이",
                  "catProductService":"_",
                  "title":"MDT 불량률",
                  "caption":"MDT / 일별추이 / {c_txt} / {g_txt}",
                  "catScope":"{c_txt}",
                  "group":"{g_txt}",
                  "dates":"2주간"
                }}, {{
                  "catIndicator":"LTE기지국통계RRC",
                  "catPresentationFormat":"일별추이",
                  "catProductService":"RRC성공률",
                  "title":"LTE기지국통계RRC",
                  "caption":"LTE기지국통계RRC / 일별추이 / RRC성공률 / {c_txt} / {g_txt}",
                  "catScope":"{c_txt}",
                  "group":"{g_txt}",
                  "dates":"2주간"
                }}
              ]
            }}
        """
    if level == "직원":
        if group.endswith("조"):
            print("DEFAULT >> 직원 조")
            tmp = default_config.format(c_txt="조별", g_txt=group)
        elif group.endswith("팀") or group.endswith("부"):
            tmp = default_config.format(c_txt="팀별", g_txt=group)
        elif group.endswith("센터"):
            tmp = default_config.format(c_txt="센터별", g_txt=group)
        else:
            tmp = default_config.format(c_txt="팀별", g_txt="강남엔지니어링부")
    else:
        if group.endswith("팀") or group.endswith("부"):
            tmp = default_config.format(c_txt="팀별", g_txt=group)
        elif group.endswith("센터"):
            tmp = default_config.format(c_txt="센터별", g_txt=group)
        else:
            tmp = default_config.format(c_txt="팀별", g_txt="강남엔지니어링부")
    return tmp
    # return db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == user_id).first()


# ------------------------------- User DashBoard Config ... -------------------------------------- #
#
# def create_dashboard_config_by_id(db: Session, id: str):
#     """
#     Dashboard Profile Create...
#     권한 별 Default Dashboard profile 설정 추가작업 필요...
#     """
#     db_board_config = models.UserDashboardConfig(owner_id=id,
#                                                  modules=json.dumps(list()))
#
#     db.add(db_board_config)
#     db.commit()
#     db.refresh(db_board_config)
#     return db_board_config
#
#
# def get_dashboard_configs(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.UserDashboardConfig).offset(skip).limit(limit).all()
#
#
# def get_dashboard_configs_by_id(db: Session, user_id: str):
#     return db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == user_id).first()
#
#
# def update_dashboard_config(id:str, db: Session, board_config: schemas.UserBoardConfig):
#     db_dashboard_config = db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == id).first()
#     if db_dashboard_config is None:
#         raise ex.NotFoundUserEx
#     dashboard_data = dashboard_schema_to_model(schema=board_config)
#
#     for k, v in dashboard_data.items():
#         setattr(db_dashboard_config, k, v)
#     db.add(db_dashboard_config)
#     db.commit()
#     db.refresh(db_dashboard_config)
#     return db_dashboard_config
#
#
# def delete_dashboard_config(db: Session, id: str):
#     db_board_config = db.query(models.UserDashboardConfig).filter(models.UserDashboardConfig.owner_id == id).first()
#
#     if db_board_config is None:
#         raise ex.NotFoundUserEx
#
#     db.delete(db_board_config)
#     db.commit()
#     return db_board_config
