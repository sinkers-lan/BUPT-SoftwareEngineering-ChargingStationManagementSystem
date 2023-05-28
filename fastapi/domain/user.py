from typing import List, Optional, Dict, Tuple
from utils.my_time import virtual_time
import utils.my_time as my_time
from enum import Enum
import utils.config as config
from service.dispatch import dispatch


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


class Key(Enum):
    your_position = "car_position"
    user_state = "car_state"
    queue_len = "queue_num"
    request_time = "request_time"
    pile_id = "pile_id"
    bill_id = "bill_id"


class ChargingInfo:
    def __init__(self):
        self.charging_info: Dict[str, Dict[Key, Optional]] = {}

    def add_car(self, car_id):
        self.charging_info[car_id] = {}

    def del_car(self, car_id):
        self.charging_info.pop(car_id)


class StateDict:
    def __init__(self):
        self.state_dict: Dict[str, UserState] = {}

    def inquire_car_state(self, car_id):
        self.state_dict.get(car_id, UserState.free)

    def change_car_state(self, car_id, state: UserState):
        self.state_dict[car_id] = state

    def del_car_state(self, car_id):
        self.state_dict.pop(car_id)

class ModeDict:
    def __int__(self):
        self.mode_dict: Dict[str, str] = {}

    def inquire_car_mode(self, car_id):
        self.mode_dict.get(car_id, -1)

    def add_car_mode(self, car_id, mode):
        self.mode_dict[car_id] = mode

    def del_car_mode(self, car_id):
        self.mode_dict.pop(car_id)


class QInfo:
    def __init__(self, mode: str, user_id: int, car_id: str, degree: float):
        self.mode = mode
        self.user_id = user_id
        self.car_id = car_id
        self.degree = degree
        self.request_time = virtual_time.get_current_time()
        if mode == "快充":
            speed = 30.0
        else:
            speed = 7.0
        self.during = (degree / speed) * 60 * 60
        self.queue_num = ""

    def assign_queue_num(self, queue_num: str):
        self.queue_num = queue_num


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

    def get_your_info(self, car_id):
        for q_info in self.q:
            if q_info.car_id == car_id:
                return q_info
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
        self.pile_id = pile_id

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
            self.timer = my_time.start_timer(first_info.during, callback=dispatch.a_car_finish,
                                             args=(self.pile_id, self.mode, car_id))
        else:
            return -1

    def end_charging(self, car_id):
        first_info = self.q[0]
        if car_id == first_info.car_id and self.state == PileState.using:
            # 手动结束充电
            self.timer.terminate()
            self.state = PileState.free
        elif car_id != first_info.car_id:
            raise Exception("You are not the fist one in the charging queue, can not end charging")
        elif self.state == PileState.using:
            raise Exception("Pile is not charging, can not end charging")

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

    def get_your_len(self, car_id):
        return self.q_queue.get_your_position(car_id)

    def add_car(self, q_info: QInfo) -> UserState:
        self.q_queue.push(q_info)
        if self.q_queue.len == 1:
            return UserState.allow
        else:
            return UserState.waiting_for_charging

    def start_charging(self, car_id):
        self.q_queue.start_charging(car_id)

    def end_charging(self, car_id):
        self.q_queue.start_charging(car_id)

    def get_end_time(self):
        return self.q_queue.end_time

    def has_vacancy(self):
        return self.q_queue.len < self.q_queue.max_len


class ChargingAreaFastOrSlow:
    def __init__(self, mode):
        self.mode = mode
        if mode == "快充":
            self.pile_num = config.FastChargingPileNum
            keys = [i * 10 + 0 for i in  range(1, config.FastChargingPileNum + 1)]
        else:
            self.pile_num = config.TrickleChargingPileNum
            keys = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]
        values = [ChargingStation(mode, i) for i in keys]
        self.pile_dict = dict(zip(keys, values))
        self.car_pile_dict: Dict[str, int] = {}

    def has_vacancy(self):
        for station in self.pile_dict.values():
            if station.has_vacancy():
                return True
        return False

    def add_car(self, pile_id, q_info: QInfo):
        self.car_pile_dict[q_info.car_id] = pile_id
        return self.pile_dict[pile_id].add_car(q_info)

    def end_charging(self, car_id):
        pass

    def dispatch(self):
        """
        选出所有充电桩中预计完成充电时间最短的的充电桩。
        由于如果充电桩队列为空，预计时间为-1，所以可以直接通过比得到取最小值得出。
        如果有预计结束时间重复的充电桩，只会给出其中一个充电桩的编号。
        :return: 充电桩编号
        """
        end_time_dict = dict([(pile.get_end_time(), pile.pile_id) for pile in self.pile_dict.values() if pile.has_vacancy()])
        earliest_end_time = min(end_time_dict.values())
        return end_time_dict[earliest_end_time]



class ChargingArea:
    def __init__(self):
        self.fast_area = ChargingAreaFastOrSlow("快充")
        self.slow_area = ChargingAreaFastOrSlow("慢充")

    def has_vacancy(self, mode):
        if mode == "快充":
            return self.fast_area.has_vacancy()
        else:
            return self.slow_area.has_vacancy()

    def add_car(self, mode, pile_id, q_info: QInfo) -> UserState:
        if mode == "快充":
            return self.fast_area.add_car(pile_id, q_info)
        else:
            return self.slow_area.add_car(pile_id, q_info)

    def dispatch(self, mode):
        if mode == "快充":
            return self.fast_area.dispatch()
        else:
            return self.slow_area.dispatch()

    def pop_car_pile_dict(self, mode, car_id):
        if mode == "快充":
            return self.fast_area.car_pile_dict.pop(car_id)
        else:
            return self.slow_area.car_pile_dict.pop(car_id)

    def get_your_pile(self, mode, car_id):
        if mode == "快充":
            return self.fast_area.car_pile_dict.get(car_id)
        else:
            return self.slow_area.car_pile_dict.get(car_id)

    def get_your_len(self, mode, car_id, pile_id):
        if mode == "快充":
            return self.fast_area.pile_dict[pile_id].get_your_len(car_id)
        else:
            return self.slow_area.pile_dict[pile_id].get_your_len(car_id)

    def get_all_len(self, mode, pile_id):
        if mode == "快充":
            return self.fast_area.pile_dict[pile_id].q_queue.len
        else:
            return self.slow_area.pile_dict[pile_id].q_queue.len


class WaitingQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode, config.WaitingAreaSize)



class WaitingArea:
    def __init__(self):
        self.fast_queue = WaitingQueue("快充")
        self.slow_queue = WaitingQueue("慢充")
        self.max_len = config.WaitingAreaSize
        self.all_len = 0
        self.fast_queue_num = 1
        self.slow_queue_num = 1

    def add_car(self, q_info: QInfo):
        if self.all_len >= self.max_len:
            raise Exception("Could not add car into waiting area")
        self.all_len += 1
        if q_info.mode == "快充":
            q_info.assign_queue_num("F" + str(self.fast_queue_num))
            self.fast_queue_num += 1
            self.fast_queue.push(q_info)
        else:
            q_info.assign_queue_num("T" + str(self.slow_queue_num))
            self.slow_queue_num += 1
            self.slow_queue.push(q_info)

    def has_vacancy(self):
        return self.all_len < self.max_len

    def has_car(self, mode):
        if mode == "快充":
            return self.fast_queue.len != 0
        else:
            return self.slow_queue.len != 0

    def call_out(self, mode) -> QInfo:
        if mode == "快充":
            return self.fast_queue.pop()
        else:
            return self.slow_queue.pop()

    def get_first(self, mode):
        if mode == "快充":
            return self.fast_queue.q[0]
        else:
            return self.slow_queue.q[0]

    def get_your_len(self, mode, car_id):
        if mode == "快充":
            return self.fast_queue.get_your_position(car_id)
        else:
            return self.slow_queue.get_your_position(car_id)

    def get_queue_len(self, mode):
        if mode == "快充":
            return self.fast_queue.len
        else:
            return self.fast_queue.len

    def get_your_info(self, mode, car_id):
        if mode == "快充":
            return self.fast_queue.get_your_info(car_id)
        else:
            return self.slow_queue.get_your_info(car_id)


class AllArea:
    def __init__(self):
        self.charging_area = ChargingArea()
        self.waiting_area = WaitingArea()

    def waiting_area_add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)

    def charging_is_vacancy(self, mode):
        is_vacancy = self.charging_area.has_vacancy(mode)
        return is_vacancy
