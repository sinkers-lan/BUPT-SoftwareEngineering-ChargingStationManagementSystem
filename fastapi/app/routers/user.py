# Fastapi
import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from fastapi import Header
from typing_extensions import Annotated

# 用于FastAPI解析json格式数据
from pydantic import BaseModel

from app.utils import utils
from app.dao import user as user_dao
from app.domain.user import UserState
from app.service import dispatch
from app.dependencies import get_token_header

router = APIRouter(
    prefix="/user",
    # tags=["user"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)
dispatching = dispatch.Dispatch()


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
async def log_out(user: LogoutUser):
    pass


class ChargingRequest(BaseModel):
    car_id: str
    request_amount: float
    request_mode: str


@router.post("/chargingRequest")
async def user_register(charging_request: ChargingRequest):
    data = dispatching.new_car_come(user_id=1, car_id=charging_request.car_id, mode=charging_request.request_mode,
                                    degree=charging_request.request_amount)
    return data


class CarId(BaseModel):
    car_id: str


@router.post("/queryCarState")
async def query_car_state(parm: CarId, authorization: Annotated[Union[str, None], Header()] = None):
    user_id = utils.decode_token(authorization)
    car_id = parm.car_id
    data = dispatching.get_car_state(car_id)
    return data


class ChangeChargingMode(BaseModel):
    car_id: str
    request_mode: str


@router.post("/changeChargingMode")
async def change_charging_mode(parm: ChangeChargingMode):
    return {
        "code": 1,
        "message": "请求成功",
        "data": {
            "car_position": 2,
            "car_state": UserState.waiting.value,
            "queue_num": 4,
            "request_time": datetime.datetime.now()
        }
    }


class ChangeChargingAmount(BaseModel):
    car_id: str
    request_amount: float


@router.post("/changeChargingAmount")
async def change_charging_amount(parm: ChangeChargingAmount):
    return {
        "code": 1,
        "message": "请求成功"
    }


@router.post("/beginCharging")
async def begin_charging(parm: CarId):
    return {
        "code": 1,
        "message": "开始充电"
    }


@router.post("/getChargingState")
async def get_charging_state(parm: CarId):
    return {
        "code": 1,
        "message": "请求成功",
        "data": {
            "car_id": "京...",
            "bill_date": "YYYY-MM-DD",
            "bill_id": 1,
            "pile_id": 20,
            "charge_amount": 27.0,
            "charge_duration": 1.5,
            "start_time": datetime.datetime.now(),
            "end_time": datetime.datetime.now(),
            "total_charge_fee": 1.1,
            "total_service_fee": 1.1,
            "total_fee": 1.1
        }
    }


@router.post("/endCharging")
async def end_charging(parm: CarId):
    return {
        "code": 1,
        "message": "充电结束"
    }


class ChangeCapacity(BaseModel):
    car_id: str
    car_capacity: float


@router.post("/changeCapacity")
async def change_capacity(parm: ChangeCapacity):
    return {
        "code": 1,
        "message": "修改成功",
        "data": {
            "car_capacity": 34.99
        }
    }


class GetTotalBill(BaseModel):
    car_id: str
    bill_date: datetime.date


@router.post("/getTotalBill")
async def get_total_bill(pram: GetTotalBill):
    return {
        "code": 1,
        "message": "查询成功",
        "data": {
            "bill_list": [
                {
                    "car_id": "京...",
                    "bill_date": "YYYY-MM-DD",
                    "bill_id": 1,
                    "pile_id": 20,
                    "charge_amount": 27.0,
                    "charge_duration": 1.5,
                    "start_time": datetime.datetime.now(),
                    "end_time": datetime.datetime.now(),
                    "total_charge_fee": 1.1,
                    "total_service_fee": 1.1,
                    "total_fee": 1.1
                },
                {}
            ]
        }
    }


class BillId(BaseModel):
    bill_id: str


@router.post("/getDetailBill")
async def get_detail_bill(pram: BillId):
    return {
        "code": 1,
        "message": "查询成功",
        "data": {
            "car_id": "京...",
            "bill_date": "YYYY-MM-DD",
            "bill_id": 1,
            "pile_id": 20,
            "charge_amount": 27.0,
            "charge_duration": 1.5,
            "start_time": datetime.datetime.now(),
            "end_time": datetime.datetime.now(),
            "total_charge_fee": 1.1,
            "total_service_fee": 1.1,
            "total_fee": 1.1
        }
    }
