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

router = APIRouter(prefix="/admin")

# 管理员密码
admin_password = '123'

# 等待队列
# state_list = [
#     {
#         'user_id': 1,
#         'car_capacity': 43.5,
#         'request_amount': 23,
#         'wait_time': 1.3,
#         'pile_id': 20,
#         'car_state': '充电区',
#         'request_mode': '快充'
#     },
#     {
#         'user_id': 2,
#         'car_capacity': 32.5,
#         'request_amount': 21,
#         'wait_time': 0.3,
#         'pile_id': 10,
#         'car_state': '充电区',
#         'request_mode': '快充'
#     },
#     {
#         'user_id': 3,
#         'car_capacity': 23.5,
#         'request_amount': 21,
#         'wait_time': 0.5,
#         'pile_id': 0,
#         'car_state': '等待区',
#         'request_mode': '慢充'
#     },
#     {
#         'user_id': 4,
#         'car_capacity': 15.5,
#         'request_amount': 6,
#         'wait_time': 1.5,
#         'pile_id': 10,
#         'car_state': '充电区',
#         'request_mode': '快充'
#     },
#     {
#         'user_id': 5,
#         'car_capacity': 12.5,
#         'request_amount': 5,
#         'wait_time': 0.5,
#         'pile_id': 0,
#         'car_state': '等待区',
#         'request_mode': '快充'
#     },
# ]

# 1.创建数据库连接
conn = my_connect.conn
# 2.创建cursor对象
cursor = my_connect.c


class PileState(Enum):
    off = '关闭'
    free = '空闲'
    using = "使用中"
    damage = "损坏"


class PileId(BaseModel):
    pile_id: int


@router.post("/powerCrash")
async def pile_broken(pram: PileId, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {'code': 0, 'message': info}
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


class Admin(BaseModel):
    password: str


@router.post("/login")
async def login(admin: Admin):
    if admin.password == admin_password:
        return {
            'code': 1,
            'message': '登录成功',
            'data': {
                'token': utils.generate_token(0)
            }
        }
    else:
        print(admin.password)
        return {
            'code': 0,
            'message': '密码错误'
        }


@router.post("/queryPileAmount")
async def query_pile_amount(authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        # 充电桩数量
        amount = config.FastChargingPileNum + config.TrickleChargingPileNum
        # 快充充电桩数量
        fast_pile_id = [i * 10 + 0 for i in range(1, config.FastChargingPileNum + 1)]
        # 慢充充电桩数量
        slow_pile_id = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]
        return {
            'code': 1,
            'message': '成功得到充电桩数量',
            'data': {
                'amount': amount,
                'fast_pile_id': [{'pile_id': i} for i in fast_pile_id],
                'slow_pile_id': [{'pile_id': i} for i in slow_pile_id]
            }
        }
    else:
        return {
            'code': 0,
            'message': info
        }


@router.post("/logout")
async def logout(authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        return {
            'code': 1,
            'message': '成功登出',
        }
    else:
        return {
            'code': 0,
            'message': info
        }


class Pile(BaseModel):
    pile_id: int


@router.post("/queryPileState")
async def query_pile_state(pile: Pile, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        data = admin_dao.getPileState(pile.pile_id)
        # print(f"return pile_id {pile.pile_id}")
        # print(datetime.datetime.now().strftime("%H:%M:%S.%f"))
        return {
            'code': 1,
            'message': '成功得到充电桩状态',
            'data': data
        }
    else:
        return {
            'code': 0,
            'message': info
        }


@router.post("/powerOn")
async def power_on(pram: Pile, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if not flag:
        return {'code': 0, 'message': info}
    state = PileState(admin_dao.get_pile_state(pram.pile_id))
    if state == PileState.damage:
        dispatching.pile_repair(pram.pile_id)
        return {'code': 1, 'message': '修复成功'}
    elif state == PileState.off:
        data = dispatching.turn_on_the_pile(pram.pile_id)
        return data
    else:
        return {'code': 0, 'message': '该充电桩已经开启'}


@router.post("/powerOff")
async def power_off(pile: Pile, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        data = dispatching.turn_off_the_pile(pile.pile_id)
        return data
    else:
        return {
            'code': 0,
            'message': '未能正常关闭充电桩'
        }


class Price(BaseModel):
    low_price: float
    mid_price: float
    high_price: float


@router.post("/setPrice")
async def set_price(price: Price, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        config.PeakRate = price.high_price
        config.NormalRate = price.mid_price
        config.OffPeakRate = price.low_price
        return {
            'code': 1,
            'message': '成功设置价格'
        }
    else:
        return {
            'code': 0,
            'message': info
        }


class Report(BaseModel):
    pile_id: int
    start_date: str
    end_date: str


@router.post("/queryReport")
async def query_report(report: Report, authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        data = admin_dao.getPileReport(report.pile_id, report.start_date, report.end_date, cursor)
        # print(data)
        return {
            'code': 1,
            'message': '成功得到充电桩报表',
            'data': data
        }
    else:
        return {
            'code': 0,
            'message': info,
        }


@router.post("/queryQueueState")
async def query_queue_state(authorization: Annotated[Union[str, None], Header()] = None):
    flag, info = utils.decode_token(authorization)
    if flag:
        return {
            'code': 1,
            'message': '成功返回队列状态',
            'data': {
                'state_list': dispatching.get_all_queue_state()
            }
        }
    else:
        return {
            'code': 0,
            'message': info
        }
