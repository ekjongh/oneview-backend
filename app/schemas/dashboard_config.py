from typing import List, Union
from pydantic import BaseModel


# class UserBoardConfigBase(BaseModel):
#     owner_id: Union[str, None]
#
#
# class ModuleConfigBase(BaseModel):
#     kpi: Union[str, None]
#     group: Union[str, None]
#
#
# class UserBoardConfig(UserBoardConfigBase):
#     modules: List[ModuleConfigBase]
class DashboardConfigIn(BaseModel):
    name: Union[str, None]
    board_module: Union[str, None]
    # update_yn: Union[bool, None]


class DashboardConfigOut(BaseModel):
    board_id: Union[int, None]
    name: Union[str, None]
    board_module: Union[str, None]
    owner_id: Union[str, None]
    update_yn: Union[bool, None]


class DashboardConfigList(BaseModel):
    board_id: Union[int, None]
    name: Union[str, None]
    owner_id: Union[str, None]
    update_yn: Union[bool, None]
