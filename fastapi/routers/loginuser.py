# Fastapi
from fastapi import APIRouter

# 用于FastAPI解析json格式数据
from pydantic import BaseModel
from typing import Optional

from utils import utils

router = APIRouter(prefix="/user")


class LoginUser(BaseModel):
    user_name: str
    password: str
    # address: Optional[str] = None       # 住址 可选字段


@router.post("/login")
async def user_login(user: LoginUser):
    """用户登录"""
    print(user.user_name, user.password)
    """验证用户名密码在数据库中是否存在"""

    response = {
        "code": 1,
        "message": "登陆成功",  # Optional
        "data": {
            "user_id": 11,
            "user_name": user.user_name,
            "token": utils.generate_token(user)
        }
    }
    return response


@router.post("/register")
async def user_register(user: LoginUser):
    """用户注册"""
    print(user.user_name, user.password)
    """验证用户名在数据库中是否有重复，如果重复则返回失败信息"""
    response = {
        "code": 1,
        "message": "登陆成功",  # Optional
        "data": {
            "user_id": 11,
            "user_name": user.user_name,
            "token": utils.generate_token(user)
        }
    }
    return response


class LogoutUser(BaseModel):
    user_name: str
    password: str


@router.post("/logout")
async def user_register(user: LogoutUser):
