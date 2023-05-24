# Fastapi
from fastapi import APIRouter

# 用于FastAPI解析json格式数据
from pydantic import BaseModel
from typing import Optional

# 用于生成token
import jwt
import datetime

router = APIRouter(prefix="/user")


class User(BaseModel):
    user_name: str
    password: str
    # address: Optional[str] = None       # 住址 可选字段


@router.post("/login")
async def login(user: User):
    print(user.user_name, user.password)
    response = {
        "code": 1,
        "message": "登陆成功",  # Optional
        "data": {
            "user_id": 11,
            "user_name": user.user_name,
            "token": generate_token(user)
        }
    }
    return response


def generate_token(user):
    """
     :param user: 用户对象
     :return: 生成的token
    """
    # 自己组织payload
    payload = {
        'user_name': user.user_name,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload=payload, key="hello_my_teammates", algorithm='HS256')
    return token
