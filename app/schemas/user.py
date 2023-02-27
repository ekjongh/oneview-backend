from typing import List, Union
from .item import Item
from pydantic import BaseModel
from .dashboard_config import ModuleConfigBase

# class ModuleConfigBase(BaseModel):
#     kpi: Union[str, None]
#     group: Union[str, None]


class UserBase(BaseModel):
    user_id: Union[str, None]
    # username: Union[str, None]
    # email: Union[str, None]
    # phone: Union[str, None]


class UserCreate(UserBase):
    user_id: Union[str, None]
    # id: Union[int, None]
    # password: Union[str, None]
    # username: Union[str, None] = None
    # email: Union[str, None] = None
    # phone: Union[str, None] = None


class UserUpdate(UserBase):
    user_id: Union[str, None] = None
    user_name: Union[str, None] = None
    email: Union[str, None] = None
    phone: Union[str, None] = None
    is_active: Union[bool, None] = None
    is_superuser: Union[bool, None] = None
    auth: Union[str, None] = None
    level: Union[str, None] = None

    group_1: Union[str, None] = None
    group_2: Union[str, None] = None
    group_3: Union[str, None] = None
    group_4: Union[str, None] = None
    # board_modules: List[ModuleConfigBase]
    board_id: Union[int, None]
    start_board_id: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": "10151032",
                "auth": "직원",
                "group_1": "네트워크부문",
                "group_2": "네트워크운용혁신담당",
                "group_3": "네트워크운용혁신담당",
                "group_4": "네트워크AI개발P-TF",

            }
        }


class UserInDBBase(UserBase):
    id: Union[int, None]
    is_active: Union[bool, None] = None
    is_superuser: Union[bool, None] = None
    items: List[Item] = []

    class Config:
        orm_mode = True


class UserOutput(UserBase):
    user_id: Union[str, None] = None
    user_name: Union[str, None] = None
    email: Union[str, None] = None
    phone: Union[str, None] = None
    group_1: Union[str, None] = None
    group_2: Union[str, None] = None
    group_3: Union[str, None] = None
    group_4: Union[str, None] = None
    is_active: Union[bool, None] = None
    is_superuser: Union[bool, None] = None
    board_id : Union[int, None] = None
    start_board_id: Union[str, None] = None
    auth: Union[str, None] = None
    level: Union[str, None] = None
    board_modules: Union[str, None] = None
    org_lvl: Union[int, None] = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": "10151032",
                "user_name": "이성현",
                "group_1": "네트워크부문",
                "group_2": "네트워크운용혁신담당",
                "group_3": "네트워크운용혁신담당",
                "group_4": "네트워크AI개발P-TF",

            }
        }


class User(UserBase):
    id: Union[int, None]

    class Config:
        schema_extra={
            "example":{
                "employee_id": "10151032",
                "auth": "직원",
                "belong_1": "네트워크부문",
                "belong_2": "네트워크운용혁신담당",
                "belong_3": "네트워크운용혁신담당",
                "belong_4": "네트워크AI개발P-TF",

            }
        }



class UserInDB(UserInDBBase):
    hashed_password: str


class UserEnc(BaseModel):
    VOC_USER_ID: Union[str, None]
    VOC_CLIENT_IP: Union[str, None]
    VOC_ORG_NM: Union[str, None]
    # username: Union[str, None]
    # email: Union[str, None]
    # phone: Union[str, None]
