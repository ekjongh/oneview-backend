from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class AddrCodeOutput(BaseModel):
    sido_nm: Union[str, None]
    gun_gu_nm: Union[str, None]
    eup_myun_dong_nm: Union[str, None]


class OrgCodeOutput(BaseModel):
    area_center_nm: Union[str, None]
    area_team_nm: Union[str, None]
    area_jo_nm: Union[str, None]
    biz_hq_nm: Union[str, None]
    oper_team_nm: Union[str, None]

