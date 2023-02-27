from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class AddrCodeOutput(BaseModel):
    cd: Union[str, None]
    val: Union[str, None]


class SubMenuCode(BaseModel):
    name: Union[str, None]
    prods: List[str] = []
    filters: List[str] = []


class MenuCodeOutput(BaseModel):
    name: Union[str, None]
    menus: List[SubMenuCode]

- 주석추가
#              기준일자 시점 데이터가 갱신된 테이블에 연관된 서비스 리스트 조회 서비스 추가
#
########################################################################################################################
from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class AddrCodeOutput(BaseModel):
    cd: Union[str, None]
    val: Union[str, None]



class SubMenuCode(BaseModel):
    name: Union[str, None]
    prods: List[str] = []
    filters: List[str] = []


class MenuCodeOutput(BaseModel):
    name: Union[str, None]
    menus: List[SubMenuCode]

