from typing import Union, List, Tuple

from pydantic import BaseModel

class VolteBtsOutput(BaseModel):
    RANK: Union[int, None]
    equip_cd: Union[str, None]         # 기지국ID
    equip_nm: Union[str, None]          # 기지국명
    cut_ratio: Union[float, None]         # 절단율
    sum_try: Union[float, None]         # 시도호
    sum_suc: Union[float, None]         # 완료호
    sum_cut: Union[float, None]         # 절단호
    # juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]

class VolteHndsetOutput(BaseModel):
    RANK: Union[int, None]
    hndset_pet_nm: Union[str, None]        # 단말기명
    cut_ratio: Union[float, None]              # 절단율
    sum_try: Union[float, None]              # 시도호
    sum_suc: Union[float, None]              # 완료호
    sum_cut: Union[float, None]              # 절단호


class VolteTrendOutput(BaseModel):
    date: Union[str, None]
    cut_rate: Union[float, None]
    fc_373: Union[float, None]
    fc_9563: Union[float, None]


class VolteEventOutput(BaseModel):
    title: Union[str, None]
    score: Union[float, None]
    score_ref: Union[float, None]
