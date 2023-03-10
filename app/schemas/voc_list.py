from typing import Union, List, Tuple

from pydantic import BaseModel


class VocListBase(BaseModel):
    base_ym: Union[str, None]
    base_date: Union[str, None]
    equip_cd0: Union[str, None]
    pass


class VocListInput(BaseModel):
    start_date: str
    end_date: str
    belong_class: str
    belong_nm: str
    pass


class VocBtsOutput(BaseModel):
    # RANK: Union[int,None]
    equip_cd: Union[str, None]         # 기지국ID
    equip_nm: Union[str, None]          # 기지국명
    voc_cnt: Union[int, None]            # VOC건수
    juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]


class VocHndsetOutput(BaseModel):
    # RANK: Union[int, None]
    hndset_pet_nm: Union[str, None]       # 단말기명
    voc_cnt: Union[int, None]             # VOC건수


class VocTrendOutput(BaseModel):
    date: Union[str, None]
    value: Union[float, None]


class VocHourTrendOutput(BaseModel):
    hour: Union[str, None]
    today_cnt: Union[float, None]
    a_week_ago_cnt:Union[int, None]
    two_weeks_ago_cnt: Union[int, None]

class VocTrendMonthOutput(BaseModel):
    date: Union[str, None]
    value: Union[float, None]
    voc_cnt: Union[int, None]
    sbscr_cnt: Union[int, None]


class VocEventOutput(BaseModel):
    title: Union[str, None]
    score: Union[float, None]
    score_ref: Union[float, None]


class VocListOutput(BaseModel):
    base_date: Union[str, None]         # 기준년원일
    sr_tt_rcp_no: Union[str, None]      # VOC접수번호
    voc_type_nm: Union[str, None]       # VOC유형
    voc_wjt_scnd_nm: Union[str, None]   # VOC2차업무유형
    voc_wjt_tert_nm: Union[str, None]   # VOC3차업무유형
    voc_wjt_qrtc_nm: Union[str, None]   # VOC4차업무유형
    svc_cont_id: Union[str, None]       # 서비스계약번호
    hndset_pet_nm: Union[str, None]     # 단말기명
    anals_3_prod_level_nm: Union[str, None]        # 분석상품레벨3
    bprod_nm: Union[str, None]          # 요금제
    # TT번호: Union[str, None]
    # TT발행주소: Union[str, None]
    equip_cd: Union[str, None]
    equip_nm: Union[str, None]          # 주기지국
    biz_hq_nm: Union[str, None]         # 주기지국센터
    oper_team_nm: Union[str, None]      # 주기지국팀
    area_jo_nm: Union[str, None]        # 주기지국조
    voc_rcp_txn: Union[str, None]
    voc_actn_txn: Union[str, None]
    tt_trt_sbst: Union[str, None]
    juso: Union[str, None]


class VocUserInfo(BaseModel):
    sr_tt_rcp_no: Union[str, None]      # VOC접수번호
    base_date: Union[str, None]         # 기준년원일
    voc_type_nm: Union[str, None]       # VOC유형
    voc_wjt_scnd_nm: Union[str, None]   # VOC2차업무유형
    voc_wjt_tert_nm: Union[str, None]   # VOC3차업무유형
    voc_wjt_qrtc_nm: Union[str, None]   # VOC4차업무유형
    svc_cont_id: Union[str, None]       # 서비스계약번호
    hndset_pet_nm: Union[str, None]     # 단말기명
    anals_3_prod_level_nm: Union[str, None]        # 분석상품레벨3
    bprod_nm: Union[str, None]          # 요금제
    svc_cont_id: Union[str, None]       # 서비스계약
    juso: Union[str, None]              # 장애발생주소
    voc_rcp_txn: Union[str, None]       # 상담처리내역
    voc_actn_txn: Union[str, None]      # voc조치내역
    tt_trt_sbst: Union[str, None]
    equip_cd: Union[str, None]          # 주기지국id
    equip_nm: Union[str, None]          # 주기지국
    latit_val: Union[str, None]         # 주기지국위도
    lngit_val: Union[str, None]         # 주기지국경도
    biz_hq_nm: Union[str, None]         # 주기지국센터
    oper_team_nm: Union[str, None]      # 주기지국팀
    area_jo_nm: Union[str, None]        # 주기지국조
    utmkx:  Union[str, None]
    utmky:  Union[str, None]
    day_utmkx: Union[str, None]
    day_utmky: Union[str, None]
    ngt_utmkx: Union[str, None]
    ngt_utmky: Union[str, None]
    equip_cd_data: Union[str, None]          # 주기지국id
    equip_nm_data: Union[str, None]          # 주기지국
    latit_val_data: Union[str, None]         # 주기지국위도
    lngit_val_data: Union[str, None]         # 주기지국경도


class BtsSummary(BaseModel):
    base_date: Union[str, None]         # 기준년원일
    svc_cont_id: Union[str, None]       # 서비스계약번호
    equip_cd: Union[str, None]          # 주기지국id
    equip_nm: Union[str, None]          # 주기지국
    latit_val: Union[str, None]
    lngit_val: Union[str, None]
    cell_cd : Union[str, None]          ###

    s1ap_cnt: Union[int, None]          # s1ap발생
    s1ap_fail_cnt: Union[int, None]     # s1ap실패

    rsrp_m105d_cnt: Union[int, None]    ###
    rsrp_m110d_cnt: Union[int, None]    ###
    rsrp_cnt: Union[int, None]        # rsrp 건수
    rsrp_sum: Union[int, None]  # rsrp 합

    rsrq_m15d_cnt: Union[int, None]      # rsrq불량
    rsrq_m17d_cnt: Union[int, None]      # rsrq불량
    rsrq_cnt: Union[int, None]      # rsrq건수
    rsrq_sum: Union[int, None]      # rsrq합

    rip_maxd_cnt: Union[int, None]       # rip 불량
    rip_sum: Union[int, None]         # rip 합
    rip_cnt: Union[int, None]         # rip 건수

    phr_m3d_cnt: Union[int, None]
    phr_mind_cnt: Union[int, None]
    phr_sum: Union[int, None]         # phr 합
    phr_cnt: Union[int, None]         # phr 건수

    nr_rsrp_cnt: Union[int, None]
    nr_rsrp_sum: Union[int, None]

    volte_try_cacnt: Union[int, None]
    volte_comp_cacnt: Union[int, None]
    volte_self_fail_cacnt: Union[int, None]  # 자망절단
    volte_other_fail_cacnt: Union[int, None]  #
    volte_fail_cacnt: Union[int, None]  #


class InbldgSummary(BaseModel):
    base_date: Union[str, None]
    svc_cont_id: Union[str, None]
    bld_id: Union[str, None]
    addr_div: Union[str, None]
    bldg_info: Union[str, None]
    adr_utmkx: Union[str, None]
    adr_utmky: Union[str, None]

    bldg_rsrp_m105d_cnt: Union[int, None]    ###
    bldg_rsrp_m110d_cnt: Union[int, None]    ###
    bldg_rsrp_cnt: Union[int, None]        # rsrp 건수
    bldg_rsrp_sum: Union[int, None]  # rsrp 합

    bldg_rip_maxd_cnt: Union[int, None]       # rip 불량
    bldg_rip_sum: Union[int, None]         # rip 합
    bldg_rip_cnt: Union[int, None]         # rip 건수

    bldg_phr_m3d_cnt: Union[int, None]
    bldg_phr_mind_cnt: Union[int, None]
    bldg_phr_sum: Union[int, None]         # phr 합
    bldg_phr_cnt: Union[int, None]         # phr 건수

    bldg_nr_rsrp_cnt: Union[int, None]
    bldg_nr_rsrp_sum: Union[int, None]

    bldg_nsinr_cnt: Union[int, None]
    bldg_nsinr_sum: Union[int, None]

    bldg_rscp_bad_cnt : Union[int, None]
    bldg_rscp_sum : Union[int, None]
    bldg_rscp_cnt : Union[int, None]

class VocSpecOutput(BaseModel):
    voc_user_info: VocUserInfo
    bts_summary: List[BtsSummary]
    inbldg_summary: List[InbldgSummary]

class VocTrendItemOutput(BaseModel):
    title: Union[str,None]
    data: List[VocTrendOutput]

class VocSummaryOutput(BaseModel):
    date: Union[str, None]
    last_time: Union[str, None]

    g5_voc: Union[int, None]
    g5_compare_1w: Union[int, None]
    g5_compare_2w: Union[int, None]
    g5_all_cnt: Union[int, None]
    g5_all_ratio: Union[float, None]

    lte_voc: Union[int, None]
    lte_compare_1w: Union[int, None]
    lte_compare_2w: Union[int, None]
    lte_all_cnt: Union[int, None]
    lte_all_ratio: Union[float, None]


class VocTrendItemMonthOutput(BaseModel):
    title: Union[str,None]
    data: List[VocTrendMonthOutput]

class VocHourTrendItemOutput(BaseModel):
    name: Union[str, None]
    data: List[int]


class VocCompareProdOutput(BaseModel):
    prod: Union[str, None]      # 분석상품3
    sum_cnt: Union[float, None]        # 금주
    sum_cnt_ref: Union[float, None]       # 전주