# Fastapi
from fastapi import APIRouter

# 用于FastAPI解析json格式数据
from pydantic import BaseModel
from typing import Optional

from utils import utils
from dao import user as user_dao
from service import dispatch

router = APIRouter(prefix="/user")


class LoginUser(BaseModel):
    user_name: str
    password: str
    # address: Optional[str] = None       # 住址 可选字段


@router.post("/login")
async def user_login(user: LoginUser):
    """用户登录"""
    print(user.user_name, user.password)
    """验证用户名密码"""
    psw = utils.hash_password(user.password)
    info = user_dao.login(user.user_name, psw)
    if info['code'] == 1:
        info['data']['token'] = utils.generate_token(info['data']['user_id'])
    return info


class LogonUser(BaseModel):
    user_name: str
    password: str
    car_id: str
    capacity: float


@router.post("/register")
async def user_register(user: LogonUser):
    """用户注册"""
    print(user.user_name, user.password, user.car_id, user.capacity)
    """验证用户名在数据库中是否有重复，如果重复则返回失败信息"""
    psw = utils.hash_password(user.password)
    info = user_dao.logon(user.user_name, psw, user.car_id, user.capacity)
    if info['code'] == 1:
        info['data']['token'] = utils.generate_token(info['data']['user_id'])
    return info


class LogoutUser(BaseModel):
    user_name: str
    password: str


@router.post("/logout")
async def user_register(user: LogoutUser):
    pass


class ChargingRequest(BaseModel):
    car_id: str
    request_amount: float
    request_mode: str


@router.post("/chargingRequest")
async def user_register(charging_request: ChargingRequest):
    
    pass
