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
        j=0
        for i in range(4-min(3, len(depts)), 4):
            setattr(db_user, f"group_{i}", depts[j])
            j = j+1
        # db_user["group_1"] = query_result["EX_POSITION_NM"]

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
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

def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    stmt = select(models.User).filter(models.User.user_id == user_id)
    query = db.execute(stmt)
    db_user = query.scalar()

    if db_user is None:
        raise ex.NotFoundUserEx

    user_data = user.dict(exclude_unset=True)

    for k, v in user_data.items():
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

