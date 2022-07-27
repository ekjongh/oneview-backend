from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta

def get_worst10_offloading_jo_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_3g_data = func.sum(func.nvl(models.Offloading.g3_total_data_qnt, 0.0))
    sum_lte_data = func.sum(func.nvl(models.Offloading.gl_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    juso = func.concat(models.Offloading.sido_nm, models.Offloading.eup_myun_dong_nm).label("juso")

    entities = [
        models.Offloading.equip_nm,
        models.Offloading.equip_cd,
        juso,
        models.Offloading.area_center_nm,
        models.Offloading.bts_oper_team_nm,
        models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        sum_3g_data,
        sum_lte_data,
        sum_5g_data,
        sum_sru_data,
        sum_total_data,
        g5_off_ratio,
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading.base_date, start_date, end_date))
    
    # if group.endswith("센터"):
        # stmt = stmt.where(models.Offloading.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Offloading.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc())
    
    query_result = db.execute(stmt).fetchmany(size=limit)

    list_offloading_offloading_bts = list(map(lambda x: schemas.OffloadingBtsOutput(
                                # 기지국명=x[0],
                                # equip_cd=x[1],
                                juso=x[0],
                                center=x[1],
                                team=x[2],
                                jo=x[3],
                                sum_3g_data = x[4],
                                sum_lte_data = x[5],
                                sum_5g_data=x[6],
                                sum_sru_data=x[7],
                                sum_total_data=x[8],
                                g5_off_ratio=x[9]
                                ), query_result))
    return list_offloading_offloading_bts


def get_offloading_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")
    
    entities = [
        models.Offloading.base_date,
    ]
    entities_groupby = [
        g5_off_ratio
    ]
    
    stmt = select(*entities, *entities_groupby)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Offloading.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt = stmt.where(models.Offloading.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading.bts_oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Offloading.area_jo_nm == group)
    
    stmt = stmt.group_by(*entities).order_by(models.Offloading.base_date.asc())
    query_result = db.execute(stmt).all()
    list_offloading_trend = list(map(lambda x: schemas.OffloadingTrendOutput(
                                date=x[0],
                                value=x[1]
                                ), query_result))
    return list_offloading_trend

def get_offloading_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")  
    in_cond = [yesterday, today]

    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + sum_sru_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")

    entities = [
        models.Offloading.base_date,
        models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        g5_off_ratio
    ]

    stmt = select([*entities, *entities_groupby], models.Offloading.base_date.in_(in_cond)).\
            group_by(*entities).order_by(models.Offloading.base_date.asc())

    stmt = stmt.where(models.Offloading.area_jo_nm == group)

    query_result = db.execute(stmt).all()

    try:
        yesterday_score = query_result[0][2]
        today_score = query_result[1][2]
        event_rate = (today_score - yesterday_score) / yesterday_score * 100
    except:
        return None

    offloading_event = schemas.OffloadingKpiOutput(
        title= "5G 오프로딩 (전일대비)",
        score= today_score,
        rate= event_rate
    )
    return offloading_event

def get_offloading_compare_by_group_date(db: Session, group: str, date:str=None):
    sum_5g_data = func.sum(func.nvl(models.Offloading.g5_total_data_qnt, 0.0))
    sum_sru_data = func.sum(func.nvl(models.Offloading.sru_total_data_qnt, 0.0))
    sum_total_data = func.sum(func.nvl(models.Offloading.total_data_qnt, 0.0))
    g5_off_ratio = (sum_5g_data + sum_sru_data) / (sum_total_data + sum_sru_data + 1e-6) * 100
    g5_off_ratio = func.round(g5_off_ratio, 4)
    g5_off_ratio = func.coalesce(g5_off_ratio, 0.0).label("g5_off_ratio")

    entities = [
        models.Offloading.base_date,
        models.Offloading.area_jo_nm
    ]
    entities_groupby = [
        g5_off_ratio
    ]
    stmt = select(*entities, *entities_groupby)

    if not date:
        date = datetime.today().strftime("%Y%m%d")
        yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")
    
    stmt = stmt.where(between(models.Offloading.base_date, yesterday, date))

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Offloading.bts_oper_team_nm == group)
        

    stmt = stmt.group_by(*entities).having(g5_off_ratio>0).order_by(g5_off_ratio.asc())
    # query_result = db.execute(stmt).all()
    pass