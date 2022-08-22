from typing import List, Union
from pydantic import BaseModel


class UserBoardConfigBase(BaseModel):
    owner_id: Union[str, None]


class ModuleConfigBase(BaseModel):
    kpi: Union[str, None]
    group: Union[str, None]


class UserBoardConfig(UserBoardConfigBase):
    modules: List[ModuleConfigBase]
