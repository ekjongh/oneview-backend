from app.schemas import BoardConfigBase, UserBoardConfig
import json


def dashboard_model_to_schema(board_config):
    owner_id = board_config.owner_id
    banners = json.loads(board_config.banners)
    cards = json.loads(board_config.cards)
    output_schema = UserBoardConfig(
            id=id,
            owner_id=owner_id,
            banners=banners,
            cards=cards
        )
    return output_schema


def dashboard_schema_to_model(schema: UserBoardConfig):

    owner_id = schema.owner_id
    banners = [dict(obj) for obj in schema.banners]
    cards = [dict(obj) for obj in schema.cards]
    banners = json.dumps(banners)
    cards = json.dumps(cards)

    dashboard_data = dict(
        owner_id=owner_id,
        banners=banners,
        cards=cards
    )
    return dashboard_data
