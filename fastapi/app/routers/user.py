# Fastapi
import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Union, Optional
from fastapi import Header
from typing_extensions import Annotated

# 用于FastAPI解析json格式数据
from pydantic import BaseModel

from app.utils import utils
from app.dao import user as user_dao
from app.dao import bill as bill_dao
from app.service.user import UserState
from app.service.user import dispatching
from app.dependencies import get_token_header

router = APIRouter(
    prefix="/user",
    # tags=["user"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


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
async def log_out(user: LogoutUser, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    pass


class ChargingRequest(BaseModel):
    car_id: str
    request_amount: float
    request_mode: str


@router.post("/chargingRequest")
async def user_register(charging_request: ChargingRequest, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    data = dispatching.new_car_come(user_id=info, car_id=charging_request.car_id, mode=charging_request.request_mode,
                                    degree=charging_request.request_amount)
    return data


class CarId(BaseModel):
    car_id: str


@router.post("/queryCarState")
async def query_car_state(parm: CarId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    car_id = parm.car_id
    data = dispatching.get_car_state(car_id)
    return data


class ChangeChargingMode(BaseModel):
    car_id: str
    request_mode: str


@router.post("/changeChargingMode")
async def change_charging_mode(parm: ChangeChargingMode, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.change_mode(parm.car_id, parm.request_mode)


class ChangeChargingAmount(BaseModel):
    car_id: str
    request_amount: float


@router.post("/changeChargingAmount")
async def change_charging_amount(parm: ChangeChargingAmount,
                                 authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.change_degree(parm.car_id, parm.request_amount)


@router.post("/beginCharging")
async def begin_charging(parm: CarId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.begin_charging(parm.car_id)


@router.post("/getChargingState")
async def get_charging_state(parm: CarId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.get_the_bill(parm.car_id)


@router.post("/endCharging")
async def end_charging(parm: CarId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.user_terminate(parm.car_id)


class ChangeCapacity(BaseModel):
    car_id: str
    car_capacity: float


@router.post("/changeCapacity")
async def change_capacity(parm: ChangeCapacity, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    # dispatching.change_degree(parm.car_id, parm.car_capacity)
    return {
        "code": 1,
        "message": "修改成功",
        "data": {
            "car_capacity": 34.99
        }
    }


class GetTotalBill(BaseModel):
    car_id: str
    bill_date: Optional[datetime.date] = None


@router.post("/getTotalBill")
async def get_total_bill(pram: GetTotalBill, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return {
        "code": 1,
        "message": "查询成功",
        "data": bill_dao.get_all_bill(pram.car_id, pram.bill_date)
    }


class BillId(BaseModel):
    bill_id: str


@router.post("/getDetailBill")
async def get_detail_bill(pram: BillId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return {
        "code": 1,
        "message": "查询成功",
        "data": bill_dao.get_bill(pram.bill_id)
    }


@router.post("/getPayBill")
async def get_pay_bill(pram: BillId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {"code": 0, "message": info}
    return dispatching.pay_the_bill(pram.bill_id)
