from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class AddrCodeOutput(BaseModel):
    cd: Union[str, None]
    val: Union[str, None]


class OrgCodeOutput2(BaseModel):
    area_center_nm: Union[str, None]
    area_team_nm: Union[str, None]
    area_jo_nm: Union[str, None]
    biz_hq_nm: Union[str, None]
    oper_team_nm: Union[str, None]


class OperTeamCode(BaseModel):
    oper_team_nm: Union[str, None]
    area_jo_nms: List[str] = []


class OrgCodeOutput(BaseModel):
    biz_hq_nm: Union[str, None]
    oper_team_nms: List[OperTeamCode]=[]


class SubMenuCode(BaseModel):
    name: Union[str, None]
    prods: List[str] = []
    filters: List[str] = []


class MenuCodeOutput(BaseModel):
    name: Union[str, None]
    menus: List[SubMenuCode]
