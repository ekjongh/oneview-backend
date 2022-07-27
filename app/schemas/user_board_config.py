from typing import List, Union
from .item import Item
from pydantic import BaseModel


class UserBoardConfigBase(BaseModel):
    owner_id: Union[str, None]
    config_nm: Union[str, None]


class BoardConfigBase(BaseModel):
    order: Union[int, None]
    kpi: Union[str, None]
    type: Union[str, None]
    group: Union[str, None]
    date: Union[str, None]


class EventConfigBase(BaseModel):
    order: Union[int, None]
    kpi: Union[str, None]
    type: Union[str, None]
    group: Union[str, None]


class UserBoardConfig(UserBoardConfigBase):
    boards: Union[List[BoardConfigBase], None]
    events: Union[List[EventConfigBase], None]
