from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, between, case,literal, and_

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

def get_user_by_id(db: Session, user_id: str):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = db.execute(stmt)
    user = query.scalar()
    # # board_module 형식 []->str 변경으로 미사용
    # # if user:
    # #     user = user_model_to_schema(user)
    return user
    # entities = [
    #     # *models.User.__table__.columns,
    #     models.User.user_id,
    #     models.User.user_name,
    #     models.User.email,
    #     models.User.phone,
    #     models.User.group_1,
    #     models.User.group_2,
    #     models.User.group_3,
    #     models.User.group_4,
    #     models.User.is_active,
    #     models.User.is_superuser,
    #     models.User.board_id,
    #     models.User.auth,
    #     models.User.level,
    #     models.DashboardConfig.board_module,
    # ]
    # stmt = select(*entities).outerjoin(models.DashboardConfig,
    #                          and_(models.User.user_id == models.DashboardConfig.owner_id,
    #                               models.User.board_id == models.DashboardConfig.board_id)).\
    #                          filter(models.User.user_id == user_id)
    # query = db.execute(stmt)
    # query_result = query.first()
    #
    # return query_result._asdict()


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


def create_user(db: Session, user: schemas.UserCreate):
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

    query = db.execute(stmt)
    query_result = query.first()

    if not query_result:
        raise HTTPException(status_code=401,detail="Bad user id")
    else :
        db_user.user_name = query_result["NAME"]
        db_user.email = query_result["EMAIL"]
        db_user.phone = query_result["MOBILE"]
        db_user.level = query_result["EX_LEVEL_NM"]
        depts = query_result["EX_POSITION_NM"].split(" ")
        for i in range(0,min(3, len(depts))):
            setattr(db_user, f"group_{i+1}", depts[i])

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_superuser(db: Session, user: schemas.UserCreate):
    db_user = models.User(user_id=user.user_id,
                          # board_modules=json.dumps(list()),
                          # username=user.username,
                          # email=user.email,
                          # phone=user.phone,
                          is_active=True,
                          is_superuser=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: schemas.UserUpdate, is_superuser:bool=False):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = db.execute(stmt)
    db_user = query.scalar()
    if db_user is None:
        raise ex.NotFoundUserEx
    elif is_superuser:
        update_key = {"user_name", "email","group_1","group_2","group_3","group_4","is_active", "is_superuser"}
    else:
        update_key = {"group_4", "board_id", "start_board_id"}
    user_data = user.dict(exclude_unset=True)

    for k, v in user_data.items():
        if k in update_key:
            setattr(db_user, k, v)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = db.execute(stmt)
    db_user = query.scalar()

    if db_user is None:
        raise ex.NotFoundUserEx
    db.delete(db_user)
    db.commit()
    return db_user

