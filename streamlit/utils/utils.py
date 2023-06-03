import datetime
from enum import Enum

import requests
import json

# HOST = "http://10.112.241.69:8002"
# HOST = "http://123.56.44.128:8002"
HOST = "http://127.0.0.1:8002"


def post(my_json: dict, path: str, token=None) -> dict:
    # print(token)
    if token is not None:
        headers = {
            # "Content-Type": "application/json",
            "Authorization": token
        }
        return requests.post(url=HOST + path, data=json.dumps(my_json), headers=headers).json()
    else:
        return requests.post(url=HOST + path, data=json.dumps(my_json)).json()


def mode_to_ft(mode: str):
    if mode == "快充":
        return "F"
    elif mode == "慢充":
        return "T"
    else:
        return mode


def ft_to_mode(mode: str):
    if mode == "F":
        return "快充"
    elif mode == "T":
        return "慢充"
    else:
        return mode


def format_datetime_s(time_stamp: float):
    return datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S")