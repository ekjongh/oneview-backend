from typing import Set, Union, List, Tuple

from pydantic import BaseModel



class DataCntCompareProdOutput(BaseModel):
    prod: Union[str, None]      # 분석상품3
    sum_cnt: Union[float, None]        # 금주
    sum_cnt_ref: Union[float, None]       # 전주

