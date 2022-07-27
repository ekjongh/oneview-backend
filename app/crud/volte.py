from sqlalchemy.orm import Session
from .. import schemas, models
from sqlalchemy import func, select, between, case
from datetime import datetime, timedelta

def get_worst10_volte_bts_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None, limit: int=10):
    # get_worst10_volte_bts_by_group_date(db: Session, group: str = None, start_date: str=None, end_date: str=None, limit: int=10):
    sum_try = func.sum(func.nvl(models.Volte.wjxbfs1, 0.0))
    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
    sum_fail = func.sum(func.nvl(models.Volte.wjxbfs3, 0.0))
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    juso = func.concat(models.Volte.sido_nm, models.Volte.eup_myun_dong_nm).label("juso")

    entities = [
        models.Volte.equip_nm,
        juso,
        # models.Volte.area_hq_nm,
        models.Volte.area_center_nm,
        models.Volte.oper_team_nm,
        models.Volte.area_jo_nm
    ]
    entities_groupby = [
        sum_try,
        sum_suc,
        sum_fail,
        sum_cut,
        cut_ratio
    ]

    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.Volte.base_date, start_date, end_date))
    
    # if group.endswith("센터"):
        # stmt = stmt.where(models.Volte.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt = stmt.where(models.Volte.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt = stmt.where(models.Volte.area_jo_nm == group)

    stmt = stmt.group_by(*entities).having(sum_try>100).order_by(cut_ratio.desc())
    
    query_result = db.execute(stmt).fetchmany(size=limit)

    list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(
                                기지국명=x[0],
                                juso=x[1],
                                center=x[2],
                                team=x[3],
                                jo=x[4],
                                sum_try=x[5],
                                sum_suc=x[6],
                                sum_fail=x[7],
                                sum_cut=x[8],
                                cut_ratio= x[9]
                                ), query_result))
    return list_worst_volte_bts

# 기존 def get_worst10_volte_bts_by_group_date()
# def get_worst10_volte_bts_by_group_date(db: Session, group: str = None, start_date: str=None, end_date: str=None, limit: int=10):
#     sum_try = func.sum(func.nvl(models.Volte.wjxbfs1, 0.0))
#     sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
#     sum_fail = func.sum(func.nvl(models.Volte.wjxbfs3, 0.0))
#     sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
#     cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
#     cut_ratio = func.round(cut_ratio, 4)
#     cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
#     juso = func.concat(models.Volte.sido_nm, models.Volte.eup_myun_dong_nm).label("juso")

#     entities = [
#         models.Volte.equip_nm,
#         juso,
#         models.Volte.oper_team_nm,
#         models.Volte.area_jo_nm1,
#     ]
#     entities_groupby = [
#         sum_try,
#         sum_suc,
#         sum_fail,
#         sum_cut,
#         cut_ratio
#     ]

#     stmt = select(*entities, *entities_groupby)
#     if not end_date:
#         end_date = start_date
        
#     if start_date:
#         stmt = stmt.where(between(models.Volte.base_date, start_date, end_date))
    
#     if group:
#         stmt = stmt.where(models.Volte.oper_team_nm == group)
    
#     stmt = stmt.group_by(*entities).having(sum_try>100).order_by(cut_ratio.desc())
    
#     query_result = db.execute(stmt).fetchmany(size=limit)

#     list_worst_volte_bts = list(map(lambda x: schemas.VolteBtsOutput(
#                                 기지국명 = x[0],
#                                 juso=x[1],
#                                 team= x[2],
#                                 jo= x[3],
#                                 sum_try=x[4],
#                                 sum_suc=x[5],
#                                 sum_fail=x[6],
#                                 sum_cut=x[7],
#                                 cut_ratio= x[8]
#                                 ), query_result))
#     return list_worst_volte_bts

def get_volte_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    
    entities_cut = [
        models.Volte.base_date,
    ]
    entities_groupby_cut = [
        cut_ratio
    ]
    
    stmt_cut = select(*entities_cut, *entities_groupby_cut)

    fc_373_cnt = func.sum(case([(models.VolteFc.fc == '373', func.nvl(models.VolteFc.wjxbfs1, 0.0))]))
    fc_9563_cnt = func.sum(case([(models.VolteFc.fc == '9563', func.nvl(models.VolteFc.wjxbfs1, 0.0))]))

    entities_fc = [
        models.VolteFc.base_date
    ]
    entities_groupby_fc = [
        fc_373_cnt,
        fc_9563_cnt,
    ]
    
    stmt_fc = select(*entities_fc, *entities_groupby_fc)
    
    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt_cut = stmt_cut.where(between(models.Volte.base_date, start_date, end_date))
        stmt_fc = stmt_fc.where(between(models.VolteFc.base_date, start_date, end_date))
    
    if group.endswith("센터"):
        stmt_cut = stmt_cut.where(models.Volte.area_center_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.area_center_nm == group)

    if group.endswith("팀") or group.endswith("부"):
        stmt_cut = stmt_cut.where(models.Volte.oper_team_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.oper_team_nm == group)
        
    if group.endswith("조"):
        stmt_cut = stmt_cut.where(models.Volte.area_jo_nm == group)
        stmt_fc = stmt_fc.where(models.VolteFc.area_jo_nm == group)
    
    stmt_cut = stmt_cut.group_by(*entities_cut).order_by(models.Volte.base_date.asc())
    stmt_fc = stmt_fc.group_by(*entities_fc).order_by(models.VolteFc.base_date.asc())

    query_result_cut = db.execute(stmt_cut).all()
    query_result_fc = db.execute(stmt_fc).all()
    query_result = list(zip(query_result_cut,query_result_fc ))
    print("query_result_fc: ", query_result_fc)
    print("query_result_cut: ", query_result_cut)
    print("MERGE: ", query_result[0])

    list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(
                                date=x[0][0],
                                cut_rate=x[0][1],
                                fc_373=x[1][1],
                                fc_9563=x[1][2],
                                ), query_result))
    return list_volte_trend

# 기존 def get_volte_trend_by_group_date()
# def get_volte_trend_by_group_date(db: Session, group: str, start_date: str=None, end_date: str=None):
#     sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
#     sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
#     cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
#     cut_ratio = func.round(cut_ratio, 4)
#     cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")
    
#     entities = [
#         models.Volte.base_date,
#     ]
#     entities_groupby = [
#         cut_ratio
#     ]
    
#     stmt = select(*entities, *entities_groupby)
    
#     if not end_date:
#         end_date = start_date
        
#     if start_date:
#         stmt = stmt.where(between(models.Volte.base_date, start_date, end_date))
    
#     stmt = stmt.where(models.Volte.oper_team_nm == group)
    
#     stmt = stmt.group_by(*entities, models.Volte.oper_team_nm).order_by(models.Volte.base_date.asc())
#     query_result = db.execute(stmt).all()
#     list_volte_trend = list(map(lambda x: schemas.VolteTrendOutput(
#                                 date=x[0],
#                                 value=x[1]
#                                 ), query_result))
#     return list_volte_trend

def get_volte_event_by_group_date(db: Session, group: str="", date:str=None):
    # today = datetime.today().strftime("%Y%m%d")
    # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

    today = date
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")  
    in_cond = [yesterday, today]

    sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
    sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
    cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
    cut_ratio = func.round(cut_ratio, 4)
    cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

    entities = [
        models.Volte.base_date,
        models.Volte.area_jo_nm
    ]
    entities_groupby = [
        cut_ratio
    ]

    stmt = select([*entities, *entities_groupby], models.Volte.base_date.in_(in_cond)).\
            group_by(*entities).order_by(models.Volte.base_date.asc())

    stmt = stmt.where(models.Volte.area_jo_nm == group)

    query_result = db.execute(stmt).all()

    try:
        yesterday_score = query_result[0][2]
        today_score = query_result[1][2]
        event_rate = (today_score - yesterday_score) / yesterday_score * 100
    except:
        return None

    volte_event = schemas.VolteEventOutput(
        title= "VoLTE 절단율(전일대비)",
        score= today_score,
        rate= event_rate
    )
    return volte_event

# 기존 Code
# def get_volte_event_by_group_date(db: Session, group: str, date:str=None):
#     # today = datetime.today().strftime("%Y%m%d")
#     # yesterday = (datetime.today() - timedelta(1)).strftime("%Y%m%d")

#     today = date
#     yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")  
#     in_cond = [yesterday, today]

#     sum_suc = func.sum(func.nvl(models.Volte.wjxbfs2, 0.0))
#     sum_cut = func.sum(func.nvl(models.Volte.wjxbfs4, 0.0))
#     cut_ratio = sum_cut / (sum_suc + 1e-6) * 100
#     cut_ratio = func.round(cut_ratio, 4)
#     cut_ratio = func.coalesce(cut_ratio, 0.0000).label("cut_ratio")

#     entities = [
#         models.Volte.base_date,
#         models.Volte.oper_team_nm
#     ]
#     entities_groupby = [
#         cut_ratio
#     ]

#     stmt = select([*entities, *entities_groupby], models.Volte.base_date.in_(in_cond)).\
#             where(models.Volte.oper_team_nm == group).group_by(*entities).order_by(models.Volte.base_date.asc())
#     query_result = db.execute(stmt).all()
    
#     try:
#         yesterday_score = query_result[0][2]
#         today_score = query_result[1][2]
#         event_rate = (today_score - yesterday_score) / yesterday_score * 100
#     except:
#         return None

#     volte_event = schemas.VolteEventOutput(
#         title= "VoLTE 절단율(전일대비)",
#         score= today_score,
#         rate= event_rate
#     )
#     return volte_event

# 일별 FC Trend
def get_volte_fc_trend_by_group_date(db: Session, start_date: str=None, end_date: str=None):
    fc_373_cnt = func.sum(case([(models.VolteFc.fc == '373', func.nvl(models.VolteFc.wjxbfs1, 0.0))]))
    fc_9563_cnt = func.sum(case([(models.VolteFc.fc == '9563', func.nvl(models.VolteFc.wjxbfs1, 0.0))]))

    entities = [
        models.VolteFc.base_date
    ]
    entities_groupby = [
        fc_373_cnt,
        fc_9563_cnt,
    ]
    
    stmt = select(*entities, *entities_groupby)

    if not end_date:
        end_date = start_date
        
    if start_date:
        stmt = stmt.where(between(models.VolteFc.base_date, start_date, end_date))
    
    stmt = stmt.group_by(*entities).order_by(models.VolteFc.base_date.asc())
    query_result = db.execute(stmt).all()

    list_volte_fc_trend = list(map(lambda x: schemas.VolteFcTrendOutput(
                                date=x[0],
                                fc_373=x[1],
                                fc_9563=x[2],
                                ), query_result))
    return list_volte_fc_trend