from enum import Enum
from fastapi import APIRouter
from fastapi import Header
from typing import Union
from typing_extensions import Annotated
from pydantic import BaseModel
from app.dao.connection import my_connect
from app.utils import utils
from app.dao import admin as admin_dao
from app.utils import config
from app.service.user import dispatching
from app.utils.my_time import virtual_time

router = APIRouter(prefix="/system")





class Rate(BaseModel):
    rate: float


@router.post("/accelerate")
async def time_accelerate(pram: Rate):
    virtual_time.accelerate(pram.rate)
    # print(virtual_time)
    return {'code': 1, 'message': '加速成功', 'data': pram.rate}


@router.post("/getTime")
async def get_time():
    # print(virtual_time)
    return {'code': 1, 'message': '获取成功', 'data': virtual_time.get_current_datetime()}

