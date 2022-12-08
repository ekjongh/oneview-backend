from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class MdtTrendOutput(BaseModel):
    date: Union[str, None]
    rsrp_bad_rate: Union[float, None]
    rsrp_mean: Union[float, None]
    rsrq_bad_rate: Union[float, None]
    rsrq_mean: Union[float, None]
    rip_bad_rate: Union[float, None]
    rip_mean: Union[float, None]
    phr_bad_rate: Union[float, None]
    phr_mean: Union[float, None]
    nr_rsrp_mean: Union[float, None]

class MdtBtsOutput(BaseModel):
    # RANK: Union[int, None]
    equip_cd: Union[str, None]         # 기지국ID
    equip_nm: Union[str, None]          # 기지국명
    rsrp_bad_rate: Union[float, None]     # RSRP불량률
    rsrp_bad_cnt: Union[int, None]
    rsrp_cnt: Union[int, None]
    rsrq_bad_rate: Union[float, None]     # RSRQ불량률
    rip_bad_rate: Union[float, None]      # RIP불량률
    phr_bad_rate: Union[float, None]      # PHR불량률
    nr_rsrp_mean: Union[float, None]     # 5G RSRP평균
    rsrp_mean: Union[float, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]

class MdtTrendItemOutput(BaseModel):
    title: Union[str,None]
    data: List[MdtTrendOutput]