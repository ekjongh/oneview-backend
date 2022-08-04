from typing import List, Union
from pydantic import BaseModel


class UserBoardConfigBase(BaseModel):
    owner_id: Union[str, None]


class BoardConfigBase(BaseModel):
    kpi: Union[str, None]
    type: Union[str, None]
    group: Union[str, None]


class EventConfigBase(BaseModel):
    kpi: Union[str, None]
    type: Union[str, None]
    group: Union[str, None]


class UserBoardConfig(UserBoardConfigBase):
    banners: Union[List[BoardConfigBase], None]
    cards: Union[List[EventConfigBase], None]
