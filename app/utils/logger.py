import json
import logging
from datetime import timedelta, datetime
from time import time
from fastapi.requests import Request
from fastapi import Body
from fastapi.logger import logger

# logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def api_logger(request: Request, response=None, error=None):
    # print("api_loger start ....")
    # print("request state: ", request.state)
    time_format = "%Y/%m/%d %H:%M:%S"
    t = time() - request.state.start
    status_code = error.status_code if error else response.status_code
    error_log = None
    user = request.state.user
    # body = await request.body()

    if error:
        if request.state.inspect:
            frame = request.state.inspect
            error_file = frame.f_code.co_filename
            error_func = frame.f_code.co_name
            error_line = frame.f_lineno
        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorFunc=error_func,
            location="{} line in {}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            msg=str(error.ex),
        )

    # email = user.email.split("@") if user and user.email else None
    user_log = dict(
        client=request.state.ip,
        user_agent= request.state.user_agent,
        user=user if user else None,
        # email="**" + email[0][2:-1] + "*@" + email[1] if user and user.email else None,
    )

    log_dict = dict(
        url=request.url.hostname + request.url.path,
        method=str(request.method),
        statusCode=status_code,
        errorDetail=error_log,
        client=user_log,
        processedTime=str(round(t * 1000, 5)) + "ms",
        datetimeUTC=datetime.utcnow().strftime(time_format),
        datetimeKST=(datetime.utcnow() + timedelta(hours=9)).strftime(time_format),
    )
    # print("logging complete")
    # print("user log: ", user_log)
    # print("log dict", log_dict)
    # print("body: ", body)
    # if body:
    #     log_dict["body"] = body

    # log 출력 형식
    formatter = logging.Formatter('[LOG / %(asctime)s / %(levelname)s]: %(name)s - %(message)s')

    # log print
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    # file_handler = logging.FileHandler('my.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    if error and error.status_code >= 500:
        logger.error(json.dumps(log_dict))
    else:
        logger.info(json.dumps(log_dict))