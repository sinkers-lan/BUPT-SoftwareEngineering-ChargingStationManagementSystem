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


class PileState(Enum):
    off = '关闭'
    free = '空闲'
    using = "使用中"
    damage = "损坏"


class PileId(BaseModel):
    pile_id: int


@router.post("/pileBroken")
async def pile_broken(pram: PileId):
    state = PileState(admin_dao.get_pile_state(pram.pile_id))
    if state == PileState.off:
        return {'code': 0, 'message': '该充电桩已经关闭，无法损坏'}
    elif state == PileState.damage:
        return {'code': 0, 'message': '该充电桩已经损坏'}
    else:
        dispatching.pile_damage(pram.pile_id)
        return {'code': 1, 'message': '损坏成功'}


@router.post("/pileRepair")
async def pile_repair(pram: PileId):
    state = PileState(admin_dao.get_pile_state(pram.pile_id))
    if state != PileState.damage:
        return {'code': 0, 'message': '该充电桩正常，无法修复'}
    else:
        dispatching.pile_repair(pram.pile_id)
        return {'code': 1, 'message': '修复成功'}


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
