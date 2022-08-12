from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class SubscrCompareOutput(BaseModel):
    단말명: Union[str, None]
    금주:Union[float, None]
    전주: Union[float, None]


