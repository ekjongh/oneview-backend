from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal

from app.errors import exceptions as ex
from app.crud.code import get_dashboard_configs_by_auth
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

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()
    # stmt = select(models.User).filter(models.User.user_id == user_id)
    # query = db.execute(stmt)
    # user = query.scalar()
    # # board_module 형식 []->str 변경으로 미사용
    # # if user:
    # #     user = user_model_to_schema(user)
    # return user


# async def get_user_by_id(db: AsyncSession, user_id: str):
#     stmt = select(models.User).filter(models.User.user_id == user_id)
#     query = await db.execute(stmt)
#     user = query.scalar()
#     # board_module 형식 []->str 변경으로 미사용
#     # if user:
#     #     user = user_model_to_schema(user)
#     return user


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
            j = j+1
        # db_user["group_1"] = query_result["EX_POSITION_NM"]

        # board_modules default :  get_default_board_modules(level, group_2, group_3)
        #   팀 직원 로그인-> 직원&팀
        #   팀장 로그인 -> 팀장&팀
        #   센터장 로그인-> 센터&센터
        #   그외 -> default.(강남엔지니어링부. 전국?)
        #   조 직원 로그인(config수정한경우) -> 직원&조
        # print("user select", db_user.level, db_user.group_3)

        db_user.auth = "직원" if db_user.level=="직원" else "팀장"

        board_config = await get_dashboard_configs_by_auth(db, db_user.auth)
        if board_config:
            db_user.board_modules = board_config.format(c_txt="팀별", g_txt=db_user.group_3)

        # print(db_user.board_modules)
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


async def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = await db.execute(stmt)
    db_user = query.scalar()

    if db_user is None:
        raise ex.NotFoundUserEx

    # board_module 형식 []->str 변경으로 미사용
    # user = user_schema_to_model(user)

    user_data = user.dict(exclude_unset=True)

    # if is_default -> default config 적용
    if user_data["is_default"]:
        board_config = await get_dashboard_configs_by_auth(db, user_data["auth"])
        if board_config:
            user_data["board_modules"] = board_config.format(c_txt="팀별", g_txt=user_data["group_3"])

    for k, v in user_data.items():
        setattr(db_user, k, v)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: Session, user_id: int):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = await db.execute(stmt)
    db_user = query.scalar()

    if db_user is None:
        raise ex.NotFoundUserEx
    await db.delete(db_user)
    await db.commit()
    return db_user



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
