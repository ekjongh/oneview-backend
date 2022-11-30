from typing import List, Union
from pydantic import BaseModel

# class UserBoardConfigBase(BaseModel):
#     owner_id: Union[str, None]
#
#
class ModuleConfigBanner(BaseModel):
    catIndicator: Union[str, None]
    catPresentationFormat: Union[str, None]
    catProductService: Union[str, None]
    catScope: Union[str, None]
    group: Union[str, None]
    dates: Union[str, None]
    targetValue: Union[str, None]
    handlesSundayAsBetweenFridayAndSunday: Union[str, None]


class ModuleConfigCard(BaseModel):
    catIndicator: Union[str, None]
    catPresentationFormat: Union[str, None]
    catProductService: Union[str, None]
    catScope: Union[str, None]
    group: Union[str, None]
    dates: Union[str, None]


class ModuleConfigBase(BaseModel):
    banners : List[ModuleConfigBanner] = []
    cards : List[ModuleConfigCard] = []
#
# class UserBoardConfig(UserBoardConfigBase):
#     modules: List[ModuleConfigBase]


class DashboardConfigIn(BaseModel):
    name: Union[str, None]
    board_module: Union[str, None]
    login_config: Union[bool, None]
    # board_module: Union[ModuleConfigBase, None]


class DashboardConfigOut(BaseModel):
    board_id: Union[int, None]
    name: Union[str, None]
    owner_id: Union[str, None]
    update_yn: Union[bool, None]
    login_config: Union[bool, None]
    board_module: Union[str, None]


class DashboardConfigList(BaseModel):
    board_id: Union[int, None]
    name: Union[str, None]
    owner_id: Union[str, None]
    update_yn: Union[bool, None]
    login_config: Union[bool, None]
