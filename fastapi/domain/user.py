from typing import List, Optional, Dict
from utils.my_time import virtual_time
import utils.my_time as my_time
from enum import Enum
import utils.config as config


class UserState(Enum):
    free = '空闲'
    waiting = '处于等候区'
    waiting_for_charging = '处于充电区'
    allow = '允许充电'
    charging = '正在充电'
    end = '结束充电'


class PileState(Enum):
    off = '关闭'
    free = '空前'
    using = "使用中"
    damage = "损坏"


class StateDict:
    def __init__(self):
        self.state_dict: Dict[str: UserState] = {}

    def inquire_car_state(self, car_id):
        self.state_dict.get(car_id, -1)

    def change_car_state(self, car_id, state: UserState):
        # if self.inquire_car_state(car_id) == -1:
        #     print("该车还没有设置状态")
        #     return -1
        self.state_dict[car_id] = state

    def del_car_state(self, car_id):
        self.state_dict.pop(car_id)


class QInfo:
    def __init__(self, mode: str, user_id: int, car_id: str, degree: float):
        self.mode = mode
        self.user_id = user_id
        self.car_id = car_id
        self.degree = degree
        self.start_time = virtual_time.get_current_time()
        if mode == "快充":
            speed = 30.0
        else:
            speed = 7.0
        self.during = (degree / speed) * 60 * 60


class QQueue:
    def __init__(self, mode: str, max_len):
        self.mode = mode
        self.len = 0
        self.max_len = max_len
        self.q: List[QInfo] = []

    def get_your_position(self, car_id):
        i = 0
        for q_info in self.q:
            if q_info.car_id == car_id:
                return i
            i += 1
        raise Exception("Can't find your car in this queue")

    def pop(self):
        if self.len == 0:
            raise Exception("The queue is empty, can not pop")
        self.len -= 1
        return self.q.pop()

    def push(self, q_info: QInfo):
        if self.len == self.max_len:
            raise Exception("The queue is full, can not push")
        self.len += 1
        self.q.append(q_info)


class ChargingStationQueue(QQueue):
    def __init__(self, mode: str, pile_id: int):
        super().__init__(mode, max_len=config.ChargingQueueLen)
        self.end_time = None
        self.state = PileState.free

    def pop(self):
        if self.len == 0:
            self.end_time = None
        self.state = PileState.free
        super().pop()  # 怎么生成详单

    def push(self, q_info: QInfo):
        # 需要设置队列的结束时间
        if self.len == 0:  # 队伍为空
            self.end_time = virtual_time.get_current_time() + q_info.during
        elif self.len == 1:
            self.end_time += q_info.during
        super().push(q_info)

    def start_charging(self, car_id):
        first_info = self.q[0]
        if car_id == first_info.car_id:
            waiting_time = 0
            for q_info in self.q:
                waiting_time += q_info.during
            self.end_time = virtual_time.get_current_time() + waiting_time
            self.state = PileState.using
            my_time.start_timer(first_info.during, callback=self.pop())
        else:
            return -1

    def end_charging(self, car_id):
        first_info = self.q[0]
        if car_id == first_info.car_id and self.state == PileState.using:
            # 手动结束充电
            pass


class ChargingStation:
    def __init__(self, mode: str, pile_id: int):
        self.mode = mode
        self.pile_id = pile_id
        if mode == "快充":
            self.speed = 30.0
        else:
            self.speed = 7.0
        self.q_queue = ChargingStationQueue(mode, pile_id)

    def get_queue_len(self):
        return self.q_queue.len

    def add_car(self, q_info: QInfo):
        self.q_queue.push(q_info)

    def start_charging(self, car_id):
        self.q_queue.start_charging(car_id)


class ChargingAreaFastOrSlow:
    def __init__(self, mode):
        self.mode = mode
        if mode == "快充":
            self.charging_station_num = config.FastChargingPileNum
            self.charging_stations = [
                ChargingStation(mode, i + 1) for i in range(self.charging_station_num)
            ]
        else:
            self.charging_station_num = config.TrickleChargingPileNum
            self.charging_stations = [
                ChargingStation(mode, i + config.FastChargingPileNum + 1) for i in range(self.charging_station_num)
            ]

    def has_vacancy(self):
        for station in self.charging_stations:
            if station.get_queue_len() < config.ChargingQueueLen:
                return True
        return False


class ChargingArea:
    def __init__(self):
        self.fast_area = ChargingAreaFastOrSlow("快充")
        self.slow_area = ChargingAreaFastOrSlow("慢充")

    def has_vacancy(self, mode):
        if mode == "快充":
            return self.fast_area.has_vacancy()
        else:
            return self.slow_area.has_vacancy()


class WaitingQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode, config.WaitingAreaSize)


class WaitingArea:
    def __init__(self):
        self.fast_queue = WaitingQueue("快充")
        self.slow_queue = WaitingQueue("慢充")
        self.max_len = config.WaitingAreaSize
        self.all_len = 0

    def add_car(self, q_info: QInfo):
        # fast_len = self.fast_queue.len
        # slow_len = self.slow_queue.len
        if self.all_len >= self.max_len:
            raise Exception("Could not add car into waiting area")
        self.all_len += 1
        if q_info.mode == "快充":
            self.fast_queue.push(q_info)
            return self.fast_queue.len
        else:
            self.slow_queue.push(q_info)
            return self.slow_queue.len

    def has_vacancy(self):
        return self.all_len < self.max_len

    def has_car(self):
        if self.all_len != 0:
            return True
        return False

    def get_cars_info(self, mode):
        if mode == "快充":
            q_queue = self.fast_queue.q
        else:
            q_queue = self.slow_queue.q
        return q_queue

    def get_time_list(self, mode):
        if mode == "快充":
            q_queue = self.fast_queue.q
        else:
            q_queue = self.slow_queue.q
        return [q_info.during for q_info in q_queue]


class AllArea:
    def __init__(self):
        self.charging_area = ChargingArea()
        self.waiting_area = WaitingArea()

    def waiting_area_add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)

    def charging_is_vacancy(self, mode):
        is_vacancy = self.charging_area.has_vacancy(mode)
        return is_vacancy
