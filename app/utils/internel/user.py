# # from app.schemas import UserBoardConfig
from app.schemas import ModuleConfigBase, ModuleConfigBanner, ModuleConfigCard

import json

def user_model_to_schema(user):
    user.board_modules = json.loads(user.board_modules)
    return user

def user_schema_to_model(user):
    user.board_modules = json.dumps([dict(obj) for obj in user.board_modules])
    return user


def boardconfig_model_to_schema(model: str):
    schema = ModuleConfigBase()
    model = json.loads(model)

    if "banners" in model.keys() :
        schema.banners = list(map(lambda x:ModuleConfigBanner(**x), model["banners"]))
    if "cards" in model.keys() :
        schema.cards = list(map(lambda x:ModuleConfigCard(**x), model["cards"]))

    return schema


def boardconfig_schema_to_model(schema:ModuleConfigBase):
    banners = [dict(obj) for obj in schema.banners]
    cards = [dict(obj) for obj in schema.cards]

    return json.dumps(dict(banners=banners, cards=cards), ensure_ascii=False)

