from typing import Union, List, Tuple

from pydantic import BaseModel

class VolteBtsOutput(BaseModel):
    rank: Union[int, None]
    기지국명: Union[str, None]
    cut_ratio: Union[float, None]
    sum_try: Union[float, None]
    sum_suc: Union[float, None]
    # sum_fail: Union[float, None]
    sum_cut: Union[float, None]
    juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]

class VolteHndsetOutput(BaseModel):
    rank: Union[int, None]
    hndset_nm: Union[str, None]
    cut_ratio: Union[float, None]
    sum_try: Union[float, None]
    sum_suc: Union[float, None]
    sum_cut: Union[float, None]


class VolteTrendOutput(BaseModel):
    date: Union[str, None]
    cut_rate: Union[float, None]
    fc_373: Union[float, None]
    fc_9563: Union[float, None]


class VolteEventOutput(BaseModel):
    title: Union[str, None]
    score: Union[float, None]
    score_ref: Union[float, None]

class VolteFcTrendOutput(BaseModel):
    date: Union[str, None]
    fc_373: Union[float, None]
    fc_9563: Union[float, None]
    # fc_sum: Union[float, None]