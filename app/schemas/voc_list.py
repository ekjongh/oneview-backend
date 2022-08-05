from typing import Union, List, Tuple

from pydantic import BaseModel


class VocListBase(BaseModel):
    base_ym: Union[str, None]
    base_date: Union[str, None]
    equip_cd0: Union[str, None]
    pass

class VocListInput(BaseModel):
    start_date: str
    end_date: str
    belong_class: str
    belong_nm: str
    pass

class VocBtsOutput(BaseModel):
    기지국명: Union[str, None]
    voc_cnt: Union[int, None]
    juso: Union[str, None]
    center: Union[str, None]
    team: Union[str, None]
    jo: Union[str, None]

class VocListOutput(BaseModel):
    기준년원일: Union[str, None]
    VOC접수번호: Union[str, None]
    VOC유형: Union[str, None]
    VOC2차업무유형: Union[str, None]
    VOC3차업무유형: Union[str, None]
    VOC4차업무유형: Union[str, None]
    서비스계약번호: Union[str, None]
    단말기명: Union[str, None]
    분석상품레벨3: Union[str, None]
    요금제: Union[str, None]
    # TT번호: Union[str, None]
    # TT발행주소: Union[str, None]
    # 상담처리내역: Union[str, None]
    주기지국: Union[str, None]
    주기지국센터: Union[str, None]
    주기지국팀: Union[str, None]
    주기지국조: Union[str, None]

class VocTrendOutput(BaseModel):
    date: Union[str, None]
    value: Union[int, None]

class VocEventOutput(BaseModel):
    title: Union[str, None]
    score: Union[float, None]
    score_ref: Union[float, None]