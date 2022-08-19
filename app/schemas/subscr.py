from typing import Set, Union, List, Tuple

from pydantic import BaseModel


class SubscrCompareOutput(BaseModel):
    hndset_pet_nm: Union[str, None]      # 단말기명
    sum_cnt: Union[float, None]        # 금주
    sum_cnt_ref: Union[float, None]       # 전주


