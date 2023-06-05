import copy
import datetime
import threading
from typing import List, Optional, Dict
from app.utils.my_time import virtual_time, VirtualTimer
from app.utils import my_time, utils
from enum import Enum
from app.utils import config
from app.dao import bill
import app.dao.user as user_dao
import app.dao.admin as admin_dao
import sqlite3


# print("service:", virtual_time)

class UserState(Enum):
    free = '空闲'
    waiting = '处于等候区'
    waiting_for_charging = '处于充电区'
    allow = '允许充电'
    charging = '正在充电'
    end = '结束充电'


class PileState(Enum):
    off = '关闭'
    free = '空闲'
    using = "使用中"
    damage = "损坏"


class Mode(Enum):
    fast = 'F'
    slow = 'T'


class Key(Enum):
    car_state = "车辆当前状态"
    queue_num = "排队号码"
    request_time = "充电请求时间"
    pile_id = "充电桩编号；当车辆在等候区时返回空值"
    request_mode = "充电模式"
    request_amount = "充电量"
    additional_bill_id = "详单编号"


class ChargingInfo:
    def __init__(self):
        self.__charging_info: Dict[str, Dict[Key, Optional]] = {}

    def add_car(self, car_id):
        self.__charging_info[car_id] = {}

    def del_car(self, car_id):
        self.__charging_info.pop(car_id)

    def get_car_state(self, car_id):
        if self.__charging_info.get(car_id, -1) == -1:
            return UserState.free
        # print("get car state", car_id, self.__charging_info[car_id][Key.car_state])
        return self.__charging_info[car_id][Key.car_state]

    def get_queue_num(self, car_id):
        return self.__charging_info[car_id][Key.queue_num]

    def get_request_time(self, car_id):
        return self.__charging_info[car_id][Key.request_time]

    def get_pile_id(self, car_id):
        return self.__charging_info[car_id].get(Key.pile_id, None)

    def get_bill_id(self, car_id):
        return self.__charging_info[car_id][Key.additional_bill_id]

    def get_mode(self, car_id):
        return self.__charging_info[car_id][Key.request_mode]

    def get_amount(self, car_id):
        return self.__charging_info[car_id][Key.request_amount]

    def get_additional_bill_id(self, car_id):
        return self.__charging_info[car_id][Key.additional_bill_id]

    def set_car_state(self, car_id, car_state):
        # print("set car state", car_id, car_state.value)
        self.__charging_info[car_id][Key.car_state] = car_state

    def set_queue_num(self, car_id, queue_num):
        self.__charging_info[car_id][Key.queue_num] = queue_num

    def set_request_time(self, car_id, request_time):
        self.__charging_info[car_id][Key.request_time] = request_time

    def set_pile_id(self, car_id, pile_id):
        self.__charging_info[car_id][Key.pile_id] = pile_id

    def set_bill_id(self, car_id, bill_id):
        self.__charging_info[car_id][Key.additional_bill_id] = bill_id

    def set_mode(self, car_id, mode):
        self.__charging_info[car_id][Key.request_mode] = mode

    def set_amount(self, car_id, amount):
        self.__charging_info[car_id][Key.request_amount] = amount

    def set_additional_bill_id(self, car_id, bill_id):
        self.__charging_info[car_id][Key.additional_bill_id] = bill_id

    def get_all_car_info(self):
        info_list = []
        for car_id in self.__charging_info.keys():
            user_id, car_capacity = user_dao.get_car_info(car_id)
            info_dict = {
                "user_id": user_id,
                "car_capacity": car_capacity,
                "request_amount": self.get_amount(car_id),
                "request_mode": self.get_mode(car_id),
                "wait_time": (virtual_time.get_current_time() - self.get_request_time(car_id)) / 3600,
                "pile_id": self.get_pile_id(car_id),
                "car_state": self.get_car_state(car_id)
            }
            info_list.append(info_dict)
        return info_list


charging_info = ChargingInfo()


class QInfo:
    def __init__(self, mode: Mode, user_id: int, car_id: str, degree: float, queue_num: str):
        self.mode = mode
        self.user_id = user_id
        self.car_id = car_id
        self.degree = degree
        self.request_time = virtual_time.get_current_time()
        if mode == Mode.fast:
            speed = 30.0
        else:
            speed = 7.0
        self.during = (degree / speed) * 60 * 60
        self.queue_num = queue_num
        charging_info.add_car(car_id)
        charging_info.set_mode(car_id, mode)
        charging_info.set_request_time(car_id, self.request_time)
        charging_info.set_queue_num(car_id, queue_num)
        charging_info.set_amount(car_id, degree)


class QInfoFactory:
    def __init__(self):
        self.__fast_number = 0
        self.__slow_number = 0

    def give_a_number(self, mode):
        if mode == Mode.fast:
            self.__fast_number += 1
            number = "F" + str(self.__fast_number)
        else:
            self.__slow_number += 1
            number = "T" + str(self.__slow_number)
        return number

    def manufacture_q_info(self, mode: Mode, user_id: int, car_id: str, degree: float):
        return QInfo(mode, user_id, car_id, degree, self.give_a_number(mode))


class QQueue:
    def __init__(self, mode: Mode, max_len):
        self.mode = mode
        self.max_len = max_len
        self.speed = 30.0 if mode == Mode.fast else 7.0
        self.__q: List[QInfo] = []

    def get_car_position(self, car_id):
        i = 0
        for q_info in self.__q:
            if q_info.car_id == car_id:
                return i
            i += 1
        raise Exception("Your are not in this queue")

    def get_len(self):
        return len(self.__q)

    def pop(self, index=0):
        if self.get_len() <= index:
            raise Exception("Index is out of queue length, can not pop")
        return self.__q.pop(index)

    def push(self, q_info: QInfo):
        if self.get_len() == self.max_len:
            raise Exception("The queue is full, can not push")
        self.__q.append(q_info)

    def get_queue(self):
        return copy.deepcopy(self.__q)

    def get_first_one(self):
        return copy.deepcopy(self.__q[0])

    def change_degree(self, index, degree):
        self.__q[index].degree = degree
        self.__q[index].during = (degree / self.speed) * 60 * 60

    def clear(self):
        self.__q.clear()


class ChargingStationQueue(QQueue):
    def __init__(self, mode: Mode):
        super().__init__(mode, max_len=config.ChargingQueueLen)

    def change_degree(self, index, degree):
        raise Exception("Can't change degree in charging area")


class ChargingStation:
    def __init__(self, mode: Mode, pile_id: int, state: PileState):
        self.mode = mode
        self.pile_id = pile_id
        if mode == Mode.fast:
            self.power = 30.0
        else:
            self.power = 7.0
        self.q_queue = ChargingStationQueue(mode)
        self.end_time: float = -1
        self.state: PileState = state
        self.timer: Optional[VirtualTimer] = None
        # admin_dao.init_pile_state(pile_id)

    def calculate_bill(self, start_time: float, charge_duration: float):
        return utils.calculate_bill(start_time, charge_duration, self.power)

    def add_car(self, q_info: QInfo) -> UserState:
        # 设置队列的结束时间
        if self.q_queue.get_len() == 0:
            self.end_time = virtual_time.get_current_time() + q_info.during
        elif 0 < self.q_queue.get_len() < self.q_queue.max_len:
            self.end_time += q_info.during
        else:
            raise Exception("The queue is full, can not add car into this charging station area")
        self.q_queue.push(q_info)
        # 返回是否允许充电
        if self.q_queue.get_len() == 1:
            return UserState.allow
        else:
            return UserState.waiting_for_charging

    def start_charging(self, car_id):
        first_info = self.q_queue.get_first_one()
        if car_id == first_info.car_id:
            # 更改充电桩状态
            self.state = PileState.using
            # 更改预计排队时间
            waiting_time = 0
            for q_info in self.q_queue.get_queue():
                waiting_time += q_info.during
            self.end_time = virtual_time.get_current_time() + waiting_time
            # 启动定时器
            self.timer = my_time.start_timer(first_info.during, callback=dispatching.a_car_finish,
                                             args=(self.pile_id, self.mode, car_id))
            # 生成账单
            during = first_info.during
            charge_fee, service_fee = self.calculate_bill(virtual_time.get_current_time(), during)
            bill_ls = bill.create_bill(car_id, self.pile_id, first_info.degree, first_info.during, charge_fee,
                                       service_fee)
            charging_info.set_bill_id(car_id, bill_ls)
        else:
            raise Exception("You are not the first one in the charging queue, can not start charging")

    def __change_bill(self, car_id):
        print("修改账单")
        end_time = virtual_time.get_current_time()
        bill_ls = charging_info.get_bill_id(car_id)
        start_time = bill.get_start_time(bill_ls)
        charge_duration = end_time - start_time
        charge_amount = charge_duration * self.power / 3600
        charge_fee, service_fee = self.calculate_bill(start_time, charge_duration)
        bill.update_bill(bill_ls, charge_fee, service_fee, end_time, charge_duration, charge_amount)
        return charge_amount

    def __end_charging(self, car_id):
        """
                分3种情况调用:
                ① 由系统定时器结束充电发起。 ② 由用户终止充电。 ③ 用户还没有开始充电时取消充电。
                :param car_id: car_id
                :return: None
                """
        # ① 由系统定时器结束充电发起。 ② 由用户终止充电。都需要停止充电
        if self.state == PileState.using:
            # 结束定时器
            self.timer.terminate()
            # 改变充电桩状态
            self.state = PileState.free
            # ② 由用户终止充电。更改账单
            if threading.current_thread().getName() != "timer":
                self.__change_bill(car_id)
        # 出队列
        position = self.q_queue.get_car_position(car_id)
        self.q_queue.pop(position)

    # 由用户或系统发起
    def normal_end_charging(self, car_id):
        self.__end_charging(car_id)
        # 更改预计排队时间
        if self.q_queue.get_len() == 0:
            self.end_time = -1
        else:
            self.end_time = virtual_time.get_current_time()
            for q_info in self.q_queue.get_queue():
                self.end_time += q_info.during
            # 把后一个车的状态设置为允许充电
            q_info = self.q_queue.get_first_one()
            charging_info.set_car_state(q_info.car_id, UserState.allow)

    def pop_car(self):
        car_id = self.q_queue.get_first_one().car_id
        self.__end_charging(car_id)
        if charging_info.get_car_state(car_id) == UserState.charging:
            self.__change_bill(car_id)

    def get_end_time(self):
        return self.end_time

    def has_vacancy(self):
        # print("充电桩状态:", self.state)
        return self.q_queue.get_len() < self.q_queue.max_len and \
            (self.state == PileState.free or self.state == PileState.using)

    def damage(self) -> List[QInfo]:
        self.end_time = -1
        self.state = PileState.damage
        q_info_list = self.q_queue.get_queue()
        # self.q_queue.clear()
        if self.state == PileState.using:
            # 结束定时器
            self.timer.terminate()
            # 更改账单
            car_id = q_info_list[0].car_id
            charge_amount = self.__change_bill(car_id)
            # 改变充电桩的累计数据
            bill_ls = charging_info.get_bill_id(car_id)
            data = bill.get_bill(bill_ls)
            admin_dao.updatePileReport(pile_id=charging_info.get_pile_id(car_id),
                                       chargeTime=data["charge_duration"],
                                       capacity=data['charge_amount'],
                                       chargeFee=data['total_charge_fee'],
                                       serviceFee=data['total_service_fee'], )
            # 更改正在充电的q_info
            request_amount = charging_info.get_amount(car_id)
            charging_info.set_amount(car_id, request_amount - charge_amount)
        # 如果队列中存在车辆，把第一个车辆的状态设置为等待充电
        if self.q_queue.get_len() > 0:
            # 更改车辆状态
            charging_info.set_car_state(q_info_list[0].car_id, UserState.waiting_for_charging)
        return q_info_list

    def repair(self):
        self.state = PileState.free
        # 如果队列中存在车辆，把第一个车辆的状态设置为允许充电
        if self.q_queue.get_len() > 0:
            q_info = self.q_queue.get_first_one()
            charging_info.set_car_state(q_info.car_id, UserState.allow)
            # 重新计算预计排队时间
            self.end_time = virtual_time.get_current_time()
            for q_info in self.q_queue.get_queue():
                self.end_time += q_info.during

    def take_out_all(self):
        q_info_list = self.q_queue.get_queue()
        if self.state == PileState.using:
            q_info_list.pop(0)
            for i in q_info_list:
                self.normal_end_charging(i.car_id)
        elif self.state == PileState.free:
            for i in q_info_list:
                self.normal_end_charging(i.car_id)
        else:
            raise Exception("Pile is damaged or closed")
        print(self.pile_id, "取出的队列长度", len(q_info_list))
        return q_info_list

    def turn_off(self):
        print("关闭充电桩", self.pile_id)
        if self.state == PileState.free:
            self.state = PileState.off
        else:
            raise Exception("Can not turn off the pile")

    def turn_on(self):
        print("打开充电桩", self.pile_id)
        if self.state == PileState.off:
            self.state = PileState.free
        else:
            raise Exception("Can not turn on the pile")


class ChargingAreaFastOrSlow:
    def __init__(self, mode):
        self.mode = mode
        if mode == Mode.fast:
            self.pile_num = config.FastChargingPileNum
            keys = [i * 10 + 0 for i in range(1, config.FastChargingPileNum + 1)]
        else:
            self.pile_num = config.TrickleChargingPileNum
            keys = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]
        state_list = []
        for pile_id in keys:
            state_list.append(admin_dao.get_pile_state(pile_id))
        values = [ChargingStation(mode, i, PileState(state)) for i, state in zip(keys, state_list)]
        self.pile_dict: Dict[int, ChargingStation] = dict(zip(keys, values))

    def has_vacancy(self):
        for station in self.pile_dict.values():
            if station.has_vacancy():
                return True
        return False

    def add_car(self, pile_id, q_info: QInfo):
        return self.pile_dict[pile_id].add_car(q_info)

    def end_charging(self, car_id):
        pile_id = charging_info.get_pile_id(car_id)
        self.pile_dict[pile_id].normal_end_charging(car_id)

    def dispatch(self):
        """
        选出所有充电桩中预计完成充电时间最短的的充电桩。
        由于如果充电桩队列为空，预计时间为-1，所以可以直接通过比得到取最小值得出。
        如果有预计结束时间重复的充电桩，只会给出其中一个充电桩的编号。
        :return: 充电桩编号
        """
        end_time_dict = dict(
            [(pile.get_end_time(), pile.pile_id) for pile in self.pile_dict.values() if pile.has_vacancy()])
        earliest_end_time = min(end_time_dict.keys())  # 选出最小时间
        return end_time_dict[earliest_end_time]  # 得到对应的充电桩号

    def begin_charging(self, car_id):
        pile_id = charging_info.get_pile_id(car_id)
        self.pile_dict[pile_id].start_charging(car_id)

    def redispatch(self):
        q_info_list = []
        for station in self.pile_dict.values():
            if station.state == PileState.using or station.state == PileState.free:
                q_info_list.extend(station.take_out_all())
        q_info_list.sort(key=lambda x: x.queue_num)
        for q_info in q_info_list:
            print("redispatch", q_info.car_id)
        return q_info_list


class ChargingArea:
    def __init__(self):
        self.fast_area = ChargingAreaFastOrSlow(Mode.fast)
        self.slow_area = ChargingAreaFastOrSlow(Mode.slow)

    def has_vacancy(self, mode):
        if mode == Mode.fast:
            return self.fast_area.has_vacancy()
        else:
            return self.slow_area.has_vacancy()

    def add_car(self, mode, pile_id, q_info: QInfo) -> UserState:
        if mode == Mode.fast:
            return self.fast_area.add_car(pile_id, q_info)
        else:
            return self.slow_area.add_car(pile_id, q_info)

    def dispatch(self, mode):
        if mode == Mode.fast:
            return self.fast_area.dispatch()
        else:
            return self.slow_area.dispatch()

    def end_charging(self, car_id: str):
        mode = charging_info.get_mode(car_id)
        if mode == Mode.fast:
            self.fast_area.end_charging(car_id)
        else:
            self.slow_area.end_charging(car_id)

    def get_your_position(self, car_id):
        mode = charging_info.get_mode(car_id)
        pile_id = charging_info.get_pile_id(car_id)
        if mode == Mode.fast:
            return self.fast_area.pile_dict[pile_id].q_queue.get_car_position(car_id)
        else:
            return self.slow_area.pile_dict[pile_id].q_queue.get_car_position(car_id)

    def begin_charging(self, car_id):
        mode = charging_info.get_mode(car_id)
        if mode == Mode.fast:
            self.fast_area.begin_charging(car_id)
        else:
            self.slow_area.begin_charging(car_id)

    def pile_damage(self, pile_id) -> List[QInfo]:
        if pile_id % 10 == 0:
            return self.fast_area.pile_dict[pile_id].damage()
        else:
            return self.slow_area.pile_dict[pile_id].damage()

    def pile_repair(self, pile_id):
        if pile_id % 10 == 0:
            self.fast_area.pile_dict[pile_id].repair()
            return Mode.fast
        else:
            self.slow_area.pile_dict[pile_id].repair()
            return Mode.slow

    def redispatch(self, mode: Mode):
        if mode == Mode.fast:
            return self.fast_area.redispatch()
        else:
            return self.slow_area.redispatch()

    def turn_off_the_pile(self, pile_id):
        if pile_id % 10 == 0:
            self.fast_area.pile_dict[pile_id].turn_off()
        else:
            self.slow_area.pile_dict[pile_id].turn_off()

    def turn_on_the_pile(self, pile_id):
        if pile_id % 10 == 0:
            self.fast_area.pile_dict[pile_id].turn_on()
            return Mode.fast
        else:
            self.slow_area.pile_dict[pile_id].turn_on()
            return Mode.slow

    def has_car(self, pile_id):
        if pile_id % 10 == 0:
            return self.fast_area.pile_dict[pile_id].q_queue.get_len() > 0
        else:
            return self.slow_area.pile_dict[pile_id].q_queue.get_len() > 0

    def pop(self, mode, pile_id):
        if mode == Mode.fast:
            return self.fast_area.pile_dict[pile_id].pop_car()
        else:
            return self.slow_area.pile_dict[pile_id].pop_car()


class WaitingQueue(QQueue):
    def __init__(self, mode: Mode):
        super().__init__(mode, config.WaitingAreaSize)


class WaitingArea:
    def __init__(self):
        self.fast_queue = WaitingQueue(Mode.fast)
        self.slow_queue = WaitingQueue(Mode.slow)
        self.max_len = config.WaitingAreaSize

    def get_all_len(self):
        return self.fast_queue.get_len() + self.slow_queue.get_len()

    def add_car(self, q_info: QInfo):
        if self.get_all_len() >= self.max_len:
            raise Exception("Could not add car into waiting area")
        if q_info.mode == Mode.fast:
            self.fast_queue.push(q_info)
        else:
            self.slow_queue.push(q_info)

    def has_vacancy(self):
        return self.get_all_len() < self.max_len

    def has_car(self, mode):
        if mode == Mode.fast:
            return self.fast_queue.get_len() != 0
        else:
            return self.slow_queue.get_len() != 0

    def call_out(self, mode) -> QInfo:
        if mode == Mode.fast:
            return self.fast_queue.pop(0)
        else:
            return self.slow_queue.pop(0)

    def get_first(self, mode):
        if mode == Mode.fast:
            return self.fast_queue.get_first_one()
        else:
            return self.slow_queue.get_first_one()

    def get_queue_len(self, mode):
        if mode == Mode.fast:
            return self.fast_queue.get_len()
        else:
            return self.slow_queue.get_len()

    def get_car_position(self, car_id):
        mode = charging_info.get_mode(car_id)
        if mode == Mode.fast:
            return self.fast_queue.get_car_position(car_id)
        else:
            return self.slow_queue.get_car_position(car_id)

    def change_degree(self, car_id, new_degree):
        mode = charging_info.get_mode(car_id)
        position: int = self.get_car_position(car_id)
        if mode == Mode.fast:
            self.fast_queue.change_degree(position, new_degree)
        else:
            self.slow_queue.change_degree(position, new_degree)

    def cancel_waiting(self, car_id):
        mode = charging_info.get_mode(car_id)
        position: int = self.get_car_position(car_id)
        if mode == Mode.fast:
            return self.fast_queue.pop(position)
        else:
            return self.slow_queue.pop(position)


class DamageArea:
    def __init__(self):
        self.queue: List[QInfo] = []
        self.mode: Optional[Mode] = None

    def add_queue(self, q_info_list: List[QInfo]):
        self.queue.extend(q_info_list)
        self.mode = q_info_list[0].mode

    def is_damage(self, mode):
        # print(self.mode, self.queue)
        return self.mode == mode

    def pop(self):
        q_info = self.queue.pop(0)
        if len(self.queue) == 0:
            self.mode = None
        return q_info


class AllArea:
    def __init__(self):
        self.charging_area = ChargingArea()
        self.waiting_area = WaitingArea()

    def waiting_area_add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)

    def charging_is_vacancy(self, mode):
        is_vacancy = self.charging_area.has_vacancy(mode)
        return is_vacancy


class Dispatch:
    def __init__(self):
        self.area: AllArea = AllArea()
        self.info: ChargingInfo = charging_info
        self.q_info_factory: QInfoFactory = QInfoFactory()
        self.damage_area: DamageArea = DamageArea()

    def get_car_state(self, car_id):
        car_state = self.info.get_car_state(car_id)
        car_position = None
        queue_num = None
        request_time = None
        pile_id = None
        mode = None
        amount = None
        if car_state == UserState.free:
            car_state = car_state.value
        elif car_state == UserState.waiting:
            car_state = car_state.value
            car_position = self.area.waiting_area.get_car_position(car_id) + 1
            queue_num = self.info.get_queue_num(car_id)
            request_time = utils.format_datetime_s(self.info.get_request_time(car_id))
            mode = self.info.get_mode(car_id)
            amount = self.info.get_amount(car_id)
        elif car_state == UserState.end:
            car_state = car_state.value
            car_position = 1
            queue_num = self.info.get_queue_num(car_id)
            request_time = utils.format_datetime_s(self.info.get_request_time(car_id))
            pile_id = self.info.get_pile_id(car_id)
            mode = self.info.get_mode(car_id)
            amount = self.info.get_amount(car_id)
        else:
            car_state = car_state.value
            car_position = self.area.charging_area.get_your_position(car_id) + 1
            queue_num = self.info.get_queue_num(car_id)
            request_time = utils.format_datetime_s(self.info.get_request_time(car_id))
            pile_id = self.info.get_pile_id(car_id)
            mode = self.info.get_mode(car_id)
            amount = self.info.get_amount(car_id)
        return {
            "code": 1,
            "message": "请求成功",
            "data": {
                "car_state": car_state,
                "car_position": car_position,
                "queue_num": queue_num,
                "request_time": request_time,
                "pile_id": pile_id,
                "request_mode": mode,
                "request_amount": amount
            }
        }

    def __add_car(self, q_info: QInfo) -> int:
        """
        添加车辆, 在用户提交充电请求或改变充电模式时调用
        :param q_info: 请求信息
        :return: car_position
        """
        mode = q_info.mode
        car_id = q_info.car_id
        # 查看对应的模式的充电桩是否有空位
        if self.area.charging_area.has_vacancy(mode):
            # 如果有，寻找一个存在空位且等待时间最短的充电桩
            pile_id = self.area.charging_area.dispatch(mode)
            # 把车直接加入充电桩队列,返回用户是否可以充电
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            # 改变用户状态
            self.info.set_car_state(car_id, user_state)
            self.info.set_pile_id(car_id, pile_id)
            # 返回用户在充电桩队列中的位置
            return self.area.charging_area.get_your_position(car_id)
        else:
            # 加入等候区
            self.area.waiting_area.add_car(q_info)
            # 改变用户状态
            self.info.set_car_state(car_id, UserState.waiting)
            # 返回用户在等候区的位置
            return self.area.waiting_area.get_car_position(car_id)

    def new_car_come(self, user_id, car_id, mode, degree):
        # 把mode从字符串转换成枚举类型
        mode = Mode(mode)
        if self.info.get_car_state(car_id) != UserState.free:
            return {"code": 0, "message": "用户当前状态不空闲，不允许提交充电请求"}
        # 先查看等候区是否有空位
        if not self.area.waiting_area.has_vacancy():
            # 如果没有空位就直接返回失败信息
            return {"code": 0, "message": "等候区已满"}
        # 在QInfo对象被创建的时候，会自动在info表中添加这个车的信息
        q_info = self.q_info_factory.manufacture_q_info(mode=mode, user_id=user_id, car_id=car_id, degree=degree)
        car_position = self.__add_car(q_info)
        return {
            "code": 1,
            "message": "请求成功",
            "data": {
                "car_position": car_position + 1,
                "car_state": self.info.get_car_state(car_id).value,
                "queue_num": self.info.get_queue_num(car_id),
                "request_time": utils.format_datetime_s(self.info.get_request_time(car_id)),
            }
        }

    def __call_out(self, pile_id, mode):
        # 把mode从字符串转换成枚举类型
        mode = Mode(mode)
        # 如果有损坏区有匹配模式待叫号的车辆
        if self.damage_area.is_damage(mode):
            # 获取到最先的用户,并出队列
            q_info = self.damage_area.pop()
            # 把他从原充电桩中一并移除
            self.area.charging_area.pop(mode, self.info.get_pile_id(q_info.car_id))
        # 如果有等候区有匹配模式待叫号的车辆
        elif self.area.waiting_area.has_car(mode):
            # 获取到最先的用户,并出队列
            q_info = self.area.waiting_area.call_out(mode)
        else:
            return
        # 放入充电桩队列
        user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
        # 改变用户状态
        self.info.set_car_state(q_info.car_id, user_state)
        self.info.set_pile_id(q_info.car_id, pile_id)

    def a_car_finish(self, pile_id, mode, car_id):
        # 把mode从字符串转换成枚举类型
        mode = Mode(mode)
        # 由充电桩发起
        print("a car finish", car_id, pile_id, mode)
        # 改变用户状态
        self.info.set_car_state(car_id, UserState.end)
        # 调用充电桩的自动结束充电接口
        self.area.charging_area.end_charging(car_id)
        # 叫号
        self.__call_out(pile_id, mode)
        # 改变充电桩的累计数据
        bill_ls = self.info.get_bill_id(car_id)
        # 由于新线程不能使用原有的数据库连接，所以需要重新获取
        conn = sqlite3.connect('SoftwareEngineering.db')
        c = conn.cursor()
        data = bill.get_bill(bill_ls, conn, c)
        admin_dao.updatePileReport(pile_id=self.info.get_pile_id(car_id),
                                   chargeTime=data["charge_duration"],
                                   capacity=data['charge_amount'],
                                   chargeFee=data['total_charge_fee'],
                                   serviceFee=data['total_service_fee'],
                                   conn=conn, c=c)

    def user_terminate(self, car_id):  # 和取消充电合并
        # 用户在不同区做不同处理
        state = self.info.get_car_state(car_id)
        if state == UserState.end:
            return {"code": 0, "message": "充电已结束"}
        elif state == UserState.charging:
            # 结束充电
            self.area.charging_area.end_charging(car_id)  # 线程是安全的，因为如果是定时器线程结束充电，会先改变用户状态
            # 改变充电桩的累计数据
            bill_ls = self.info.get_bill_id(car_id)
            data = bill.get_bill(bill_ls)
            admin_dao.updatePileReport(pile_id=self.info.get_pile_id(car_id),
                                       chargeTime=data["charge_duration"],
                                       capacity=data['charge_amount'],
                                       chargeFee=data['total_charge_fee'],
                                       serviceFee=data['total_service_fee'], )
            # 改变用户状态
            self.info.set_car_state(car_id, UserState.end)
            # 叫号
            pile_id = self.info.get_pile_id(car_id)
            mode = self.info.get_mode(car_id)
            self.__call_out(pile_id, mode)
            # 更改充电桩状态
            admin_dao.changePileState(pile_id, PileState.free.value)
            return {"code": 1, "message": "成功结束充电"}
        elif state == UserState.waiting_for_charging or state == UserState.allow:
            # 取消充电
            self.area.charging_area.end_charging(car_id)
            # 叫号
            pile_id = self.info.get_pile_id(car_id)
            mode = self.info.get_mode(car_id)
            self.__call_out(pile_id, mode)
            # 改变用户状态
            self.info.del_car(car_id)
            return {"code": 1, "message": "成功取消充电"}
        elif state == UserState.waiting:
            # 取消充电
            self.area.waiting_area.cancel_waiting(car_id)
            # 改变用户状态
            self.info.del_car(car_id)
            return {"code": 1, "message": "成功取消充电"}
        else:
            return {"code": 0, "message": "用户处于空闲状态，无法取消充电"}

    def change_degree(self, car_id, degree):
        state = self.info.get_car_state(car_id)
        if state != UserState.waiting:
            return {"code": 0, "message": "用户不在等候区，无法修改充电量"}
        self.area.waiting_area.change_degree(car_id, degree)
        self.info.set_amount(car_id, degree)
        return {"code": 1, "message": "请求成功"}

    def change_mode(self, car_id, mode):
        # 把mode从字符串转换成枚举类型
        mode = Mode(mode)
        state = self.info.get_car_state(car_id)
        if state != UserState.waiting:
            return {"code": 0, "message": "用户不在等候区，无法修改充模式"}
        old_mode = self.info.get_mode(car_id)
        if old_mode == mode:
            return {"code": 0, "message": "充电模式没有改变"}
        # 取消等待
        q_info = self.area.waiting_area.cancel_waiting(car_id)
        # 更改模式
        q_info.mode = mode
        self.info.set_mode(car_id, mode)
        # 重新派号
        q_info.queue_num = self.q_info_factory.give_a_number(mode)
        self.info.set_queue_num(car_id, q_info.queue_num)
        # 加入车辆
        car_position = self.__add_car(q_info)
        return {
            "code": 1,
            "message": "修改请求成功",
            "data": {
                "car_position": car_position + 1,
                "car_state": self.info.get_car_state(car_id).value,
                "queue_num": self.info.get_queue_num(car_id),
                "request_time": utils.format_datetime_s(self.info.get_request_time(car_id)),
            }
        }

    def begin_charging(self, car_id):
        state = self.info.get_car_state(car_id)
        if state != UserState.allow:
            return {"code": 0, "message": "用于状态不处于允许充电状态"}
        self.area.charging_area.begin_charging(car_id)
        admin_dao.changePileState(self.info.get_pile_id(car_id), PileState.using.value)
        self.info.set_car_state(car_id, UserState.charging)
        return {"code": 1, "message": "请求成功"}

    def get_the_bill(self, car_id):
        state = self.info.get_car_state(car_id)
        if state != UserState.end and state != UserState.charging:
            return {"code": 0, "message": "用户不处于结束充电状态或充电状态"}
        bill_ls = self.info.get_bill_id(car_id)
        data = bill.get_bill(bill_ls)
        return {"code": 1, "message": "查询成功", "data": data}

    def pay_the_bill(self, bill_ls):
        car_id = bill.get_car_id(bill_ls)
        state = self.info.get_car_state(car_id)
        if state != UserState.end and state != UserState.free:
            return {"code": 0, "message": "用户不处于结束充电状态或空闲状态"}
        ok, info = bill.pay_the_bill(bill_ls)
        if not ok:
            return {"code": 0, "message": info}
        if state == UserState.end:
            self.info.del_car(car_id)
        return {"code": 1, "message": "支付成功"}

    def pile_damage(self, pile_id):
        # 快充充电桩数量
        fast_pile_id = [i * 10 + 0 for i in range(1, config.FastChargingPileNum + 1)]
        # 慢充充电桩数量
        slow_pile_id = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]
        total_pile_id = fast_pile_id + slow_pile_id
        # 询问每一个充电桩的状态
        for pile in total_pile_id:
            state = admin_dao.get_pile_state(pile)
            if state == PileState.damage.value:
                return {"code": 0, "message": "已经有充电桩损坏，只考虑单一充电桩损坏的情况"}
        # 通知充电区更改充电桩状态，结束正在充电的车并生成账单，得到充电队列
        q_info_list = self.area.charging_area.pile_damage(pile_id)
        # 更改充电桩状态
        admin_dao.changePileState(pile_id, PileState.damage.value)
        # 如果同种模式的充电桩还有空位
        mode = Mode.fast if pile_id % 10 == 0 else Mode.slow
        while self.area.charging_area.has_vacancy(mode) and q_info_list:
            # 将充电队列中的车加入到充电区
            q_info = q_info_list.pop(0)
            # 将原队伍中的信息删除
            self.area.charging_area.pop(mode, pile_id)
            # 将车加入新充电桩
            self.__add_car(q_info)
        if q_info_list:
            # 把充电队列加入damage区
            self.damage_area.add_queue(q_info_list)
        return {"code": 1, "message": "请求成功"}

    def pile_repair(self, pile_id):
        # 通知损坏的充电桩更改状态为空闲
        mode = self.area.charging_area.pile_repair(pile_id)
        admin_dao.changePileState(pile_id, PileState.free.value)
        # 将所有同mode的充电区中不在充电的车的q_info队列取出
        q_info_list = self.area.charging_area.redispatch(mode)
        # 把充电队列加入到各个充电桩中
        q_info_list.sort(key=lambda x: x.request_time)
        for q_info in q_info_list:
            print(q_info)
            self.__add_car(q_info)
        # 由于可用的充电桩增加，所以从从等候区叫号
        while self.area.charging_area.has_vacancy(mode) and self.area.waiting_area.has_car(mode):
            # 获取到分配的充电桩
            pile_id = self.area.charging_area.dispatch(mode)
            # 获取到最先的用户,并出队列
            q_info = self.area.waiting_area.call_out(mode)
            # 把车加入充电桩队列,返回用户是否可以充电
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            # 改变用户状态
            self.info.set_car_state(q_info.car_id, user_state)
            self.info.set_pile_id(q_info.car_id, pile_id)
        return {"code": 1, "message": "请求成功"}

    def get_all_queue_state(self):
        return self.info.get_all_car_info()

    def turn_off_the_pile(self, pile_id):
        state = PileState(admin_dao.get_pile_state(pile_id))
        if state == PileState.free and not self.area.charging_area.has_car(pile_id):
            if admin_dao.changePileState(pile_id, '关闭') == 0:
                return {"code": 0, "message": "充电桩关闭失败"}
            self.area.charging_area.turn_off_the_pile(pile_id)
            return {"code": 1, "message": "请求成功"}
        else:
            return {"code": 0, "message": "充电桩不处于空闲状态，或车辆队伍中存在车辆，无法关闭"}

    def turn_on_the_pile(self, pile_id):
        state = PileState(admin_dao.get_pile_state(pile_id))
        if state == PileState.off:
            if admin_dao.changePileState(pile_id, '空闲') == 0:
                return {"code": 0, "message": "充电桩开启失败"}
            mode = self.area.charging_area.turn_on_the_pile(pile_id)
            while self.area.waiting_area.has_car(mode):
                # 获取到最先的用户,并出队列
                q_info = self.area.waiting_area.call_out(mode)
                # 把车加入充电桩队列,返回用户是否可以充电
                user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
                # 改变用户状态
                print(q_info.car_id, user_state)
                self.info.set_car_state(q_info.car_id, user_state)
                self.info.set_pile_id(q_info.car_id, pile_id)
            return {"code": 1, "message": "请求成功"}
        else:
            return {"code": 0, "message": "充电桩不处于关闭状态，无法开启"}


dispatching = Dispatch()
