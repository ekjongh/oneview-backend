from app.schemas import BoardConfigBase, UserBoardConfig

def dashboard_model_to_schema(board_config):
    owner_id = board_config.owner_id
    config_nm = board_config.config_nm

    boards = []
    events = []

    board_list = [
                    (board_config.dashboard_kpi_1, board_config.dashboard_type_1,
                     board_config.dashboard_group_1, board_config.dashboard_date_1),
                    (board_config.dashboard_kpi_2, board_config.dashboard_type_2,
                     board_config.dashboard_group_2, board_config.dashboard_date_2),
                    (board_config.dashboard_kpi_3, board_config.dashboard_type_3,
                     board_config.dashboard_group_3, board_config.dashboard_date_3),
                    (board_config.dashboard_kpi_4, board_config.dashboard_type_4,
                     board_config.dashboard_group_4, board_config.dashboard_date_4),
                    (board_config.dashboard_kpi_5, board_config.dashboard_type_5,
                     board_config.dashboard_group_5, board_config.dashboard_date_5),
                    (board_config.dashboard_kpi_6, board_config.dashboard_type_6,
                     board_config.dashboard_group_6, board_config.dashboard_date_6)
                ]
    event_list = [
                    (board_config.event_kpi_1, board_config.event_type_1, board_config.event_group_1),
                    (board_config.event_kpi_2, board_config.event_type_2, board_config.event_group_2),
                    (board_config.event_kpi_3, board_config.event_type_3, board_config.event_group_3)
                ]

    for idx, board in enumerate(board_list):
        if board[0] is None:
            continue
        board_tmp = BoardConfigBase(
                                        order= idx+1,
                                        kpi= board[0],
                                        type= board[1],
                                        group= board[2],
                                        date= board[3]
                                    )
        boards.append(board_tmp)

    for idx, event in enumerate(event_list):
        if event[0] is None:
            continue
        event_tmp = BoardConfigBase(
                                        order= idx+1,
                                        kpi= event[0],
                                        type= event[1],
                                        group= event[2]
                                    )
        events.append(event_tmp)
    output_schema = UserBoardConfig(
            owner_id=owner_id,
            config_nm=config_nm,
            boards=boards,
            events=events
        )
    return output_schema


def dashboard_schema_to_model(update_model, board_config: UserBoardConfig):
    result = update_model
    
    owner_id = board_config.owner_id
    config_nm = board_config.config_nm
    id = owner_id + "_" + config_nm

    boards = board_config.boards
    events = board_config.events

    user_data = {}
    user_data["id"] = id
    user_data["owner_id"] = owner_id
    user_data["config_nm"] = config_nm

    for board in boards:
        user_data[f"dashboard_kpi_{board.order}"] = board.kpi
        user_data[f"dashboard_type_{board.order}"] = board.type
        user_data[f"dashboard_group_{board.order}"] = board.group
        user_data[f"dashboard_date_{board.order}"] = board.date

    for event in events:
        user_data[f"event_kpi_{event.order}"] = event.kpi
        user_data[f"event_type_{event.order}"] = event.type
        user_data[f"event_group_{event.order}"] = event.group

    for k, v in user_data.items():
        setattr(result, k, v)
    return result
