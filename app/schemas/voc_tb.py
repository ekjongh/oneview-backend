from typing import Union, List, Tuple

from pydantic import BaseModel

#
# class VocBase(BaseModel):
#     base_ym: Union[str, None]
#     voc_wjt_qrtc_nm : Union[str, None]
#     equip_cd: Union[str, None]
#     sr_tt_rcp_no: Union[str, None]
#     base_date: Union[str, None]
#     sbt_bts_cd: Union[str, None]
#
#
# class Voc(VocBase):
#
#     class Config:
#         orm_mode = True
#
#
# class BtsBase(BaseModel):
#     equip_nm: Union[str, None]
#     cell_cd: Union[str, None]
#     oper_team_nm: Union[str, None]
#     addr_dtl: Union[str, None]
#     bld_flor: Union[str, None]
#     sbt_bts_cd: Union[str, None]
#     biz_hq_nm: Union[str, None]


# class Bts(BtsBase):
#
#     class Config:
#         orm_mode = True

# 최종적으로 보내줄 api 규격.
# class JoinVoc(BaseModel):
#     # base_ym: Union[str, None]
#     sr_tt_rcp_no: Union[str, None]
#     voc_wjt_qrtc_nm : Union[str, None]
#     equip_cd: Union[str, None]
#     base_date: Union[str, None]
#     sbt_bts_cd: Union[str, None]
#     equip_nm: Union[str, None]
#     cell_cd: Union[str, None]
#     biz_hq_nm: Union[str, None]
#     oper_team_nm: Union[str, None]
#     addr_dtl: Union[str, None]
#     bld_flor: Union[str, None]
#     sbt_bts_cd: Union[str, None]



# class JoinVoc(BaseModel):
#     results: List[Tuple[Voc, Bts]]

#     class Config:
#         orm_mode = True