from app import schemas

def offloading_model_to_schema_output(keys, model):
    list_offloading_offloading_bts = list(map(lambda x: schemas.OffloadingBtsOutput(
        # 기지국명=x[0],
        # equip_cd=x[1],
        juso=x[0],
        center=x[1],
        team=x[2],
        jo=x[3],
        sum_3g_data=x[4],
        sum_lte_data=x[5],
        sum_5g_data=x[6],
        sum_sru_data=x[7],
        sum_total_data=x[8],
        g5_off_ratio=x[9]
    ), query_result))
    pass