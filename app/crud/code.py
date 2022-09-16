from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case,literal
from datetime import datetime, timedelta


def get_addr_code_all(db: Session ):
    entities = [
        models.AddrCode.sido_nm,
        models.AddrCode.gun_gu_nm,
        models.AddrCode.eup_myun_dong_nm,
    ]
    stmt = select(*entities)
    # print(stmt)

    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_code = list(map(lambda x: schemas.AddrCodeOutput(**dict(zip(query_keys, x))), query_result))
    return list_code


def get_org_code_all(db: Session):
    entities = [
        models.OrgCode.area_center_nm,
        models.OrgCode.area_team_nm,
        models.OrgCode.area_jo_nm,
        models.OrgCode.biz_hq_nm,
        models.OrgCode.oper_team_nm,
    ]
    stmt = select(*entities)

    query = db.execute(stmt)
    query_result = query.fetchall()
    query_keys = query.keys()

    list_code = list(map(lambda x: schemas.OrgCodeOutput(**dict(zip(query_keys, x))), query_result))
    return list_code

