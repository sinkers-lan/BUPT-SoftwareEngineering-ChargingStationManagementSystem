from fastapi import Header, HTTPException
from typing_extensions import Annotated
from typing import Union
import time

import jwt
import datetime
import hashlib


def generate_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload=payload, key="hello_my_teammates", algorithm='HS256')
    return token


def decode_token(token):
    try:
        data = jwt.decode(token, key="hello_my_teammates", algorithms='HS256')
    except jwt.DecodeError:
        print("token解析失败")
        return False
    exp = data.pop('exp')
    if time.time() > exp:
        print('token已失效')
        return False
    return data.pop('user_id')


async def get_token_header(authorization: Annotated[Union[str, None], Header()] = None):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")
