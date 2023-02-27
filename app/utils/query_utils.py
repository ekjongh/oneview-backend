
from typing import List


def to_dict(model, *args, exclude: List = None):
    q_dict = {}
    for c in model.__table__.columns:
        if not args or c.name in args:
            if not exclude or c.name not in exclude:
                q_dict[c.name] = getattr(model, c.name)

    return q_dict

# 주파수밴드를 equipcd 2자리로 구분(worst기지국 필터에 사용)
def band_to_equipcd2(bands:str):
    band_dict = {
        "LTE_1.8(10M)": "RC",
        "LTE_1.8(20M)": "RR",
        "LTE_1.8(20+10M)": "RQ",
        "LTE_900": "RN",
        "LTE_2.1": "RT",
        "5G_3.5": ["NR", "NP", "NF", "NU", "NI", "ND"],
        "5G_28": "NW",
    }
    band_list = bands.split("|")
    equip_list = []
    for band in band_list:
        val = band_dict[band]
        if type(val) == list:
            for v in val:
                equip_list.append(v)
        else:
            equip_list.append(val)

    return equip_list
