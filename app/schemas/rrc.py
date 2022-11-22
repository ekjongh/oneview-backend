from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class RrcTrendOutput(BaseModel):
    date: Union[str, None]
    rrc_try: Union[float, None]
    rrc_rate: Union[float, None]
    prbusage_mean: Union[float, None]


class RrcBtsOutput(BaseModel):
    # RANK: Union[int, None]
    equip_cd: Union[str, None]         # 기지국ID
    equip_nm: Union[str, None]          # 기지국명
    rrc_try: Union[float, None]
    rrc_suc: Union[float, None]
    rrc_rate: Union[float, None]
    prbusage_mean: Union[float, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]


class RrcTrendItemOutput(BaseModel):
    title: Union[str,None]
    data: List[RrcTrendOutput]