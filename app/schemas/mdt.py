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
    rank: Union[int, None]
    equip_cd: Union[str, None]
    기지국명: Union[str, None]
    rsrp_bad_rate: Union[float, None]
    rsrq_bad_rate: Union[float, None]
    rip_bad_rate: Union[float, None]
    phr_bad_rate: Union[float, None]
    nr_rsrp_mean: Union[float, None]

