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
    RANK: Union[int,None]
    equip_cd: Union[str, None]         # 기지국ID
    equip_nm: Union[str, None]          # 기지국명
    voc_cnt: Union[int, None]            # VOC건수
    # juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]


class VocHndsetOutput(BaseModel):
    RANK: Union[int, None]
    hndset_pet_nm: Union[str, None]       # 단말기명
    voc_cnt: Union[int, None]             # VOC건수


class VocTrendOutput(BaseModel):
    date: Union[str, None]
    value: Union[float, None]

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
    # 상담처리내역: Union[str, None]
    equip_nm: Union[str, None]          # 주기지국
    biz_hq_nm: Union[str, None]         # 주기지국센터
    oper_team_nm: Union[str, None]      # 주기지국팀
    area_jo_nm: Union[str, None]        # 주기지국조


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
    equip_cd: Union[str, None]          # 주기지국id
    equip_nm: Union[str, None]          # 주기지국
    latit_val: Union[str, None]         # 주기지국위도
    lngit_val: Union[str, None]         # 주기지국경도
    biz_hq_nm: Union[str, None]         # 주기지국센터
    oper_team_nm: Union[str, None]      # 주기지국팀
    area_jo_nm: Union[str, None]        # 주기지국조
    utmkx:  Union[str, None]
    utmky:  Union[str, None]

class BtsSummary(BaseModel):
    base_date: Union[str, None]         # 기준년원일
    svc_cont_id: Union[str, None]       # 서비스계약번호
    equip_cd: Union[str, None]          # 주기지국id
    equip_nm: Union[str, None]          # 주기지국
    latit_val: Union[str, None]
    lngit_val: Union[str, None]
    s1ap_fail_cnt: Union[int, None]
    rsrp_bad_cnt: Union[int, None]
    rsrq_bad_cnt: Union[int, None]
    rip_cnt: Union[int, None]
    new_phr_m3d_cnt: Union[int, None]
    phr_cnt: Union[int, None]
    nr_rsrp_cnt: Union[int, None]
    volte_self_fail_cacnt: Union[int, None]



class VocSpecOutput(BaseModel):
    voc_user_info: VocUserInfo
    bts_summary: List[BtsSummary]
