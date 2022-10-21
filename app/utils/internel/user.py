# # from app.schemas import UserBoardConfig
import json

def user_model_to_schema(user):
    user.board_modules = json.loads(user.board_modules)
    return user

def user_schema_to_model(user):
    user.board_modules = json.dumps([dict(obj) for obj in user.board_modules])
    return user

#
# def dashboard_model_to_schema(board_config):
#     owner_id = board_config.owner_id
#     modules = json.loads(board_config.modules)
#     output_schema = UserBoardConfig(
#             id=id,
#             owner_id=owner_id,
#             modules=modules,
#         )
#     return output_schema
#
#
# def dashboard_schema_to_model(schema: UserBoardConfig):
#
#     owner_id = schema.owner_id
#     modules = [dict(obj) for obj in schema.modules]
#     modules = json.dumps(modules)
#
#     dashboard_data = dict(
#         owner_id=owner_id,
#         modules=modules,
#     )
#     return dashboard_data
