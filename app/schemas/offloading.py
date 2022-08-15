from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class offloadingCompare(BaseModel):
    group: Union[str, None]
    past_value: Union[float, None]
    current_value: Union[float, None]

class OffloadingTrendOutput(BaseModel):
    date: Union[str, None]
    value: Union[float, None]


class OffloadingEventOutput(BaseModel):
    title: Union[str, None]
    score: Union[float, None]
    score_ref: Union[float, None]

class OffloadingHndsetOutput(BaseModel):
    rank: Union[int, None]
    hndset_nm: Union[str, None]
    # sum_3g_data: Union[float, None]
    # sum_lte_data: Union[float, None]
    # sum_5g_data: Union[float, None]
    # sum_sru_data: Union[float, None]
    # sum_total_data: Union[float, None]
    g5_off_ratio: Union[float, None]

class OffloadingBtsOutput(BaseModel):
    rank: Union[int, None]
    기지국명: Union[str, None]
    equip_cd: Union[str, None]
    juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]
    sum_3g_data: Union[float, None]
    sum_lte_data: Union[float, None]
    sum_5g_data: Union[float, None]
    sum_sru_data: Union[float, None]
    sum_total_data: Union[float, None]
    g5_off_ratio: Union[float, None]

class OffloadingCompareOutput(BaseModel):
    groups: Set[str] = set()
    type: Union[str, None]
    values: Union[List[offloadingCompare], None] = None