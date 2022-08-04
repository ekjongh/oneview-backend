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


def dashboard_schema_to_model(update_model, schema: UserBoardConfig):
    result = update_model
    
    owner_id = schema.owner_id
    banners = json.dumps(schema.banners)
    cards = json.dumps(schema.cards)

    user_data = dict(
        owner_id=owner_id,
        banners=banners,
        cards=cards
    )
    for k, v in user_data.items():
        setattr(result, k, v)
    return result
