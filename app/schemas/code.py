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

