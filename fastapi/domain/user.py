import copy
from typing import List, Optional, Dict, Tuple
from utils.my_time import virtual_time, VirtualTimer
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
    car_state = "车辆当前状态"
    queue_num = "排队号码"
    request_time = "充电请求时间"
    pile_id = "充电桩编号；当车辆在等候区时返回空值"
    request_mode = "充电模式"
    additional_bill_id = "详单编号"


class ChargingInfo:
    def __init__(self):
        self.charging_info: Dict[str, Dict[Key, Optional]] = {}

    def add_car(self, car_id):
        self.charging_info[car_id] = {}

    def del_car(self, car_id):
        self.charging_info.pop(car_id)

    def get_car_state(self, car_id):
        if self.charging_info.get(car_id, -1) == -1:
            return UserState.free
        return self.charging_info[car_id][Key.car_state]

    def get_queue_num(self, car_id):
        return self.charging_info[car_id][Key.queue_num]

    def get_request_time(self, car_id):
        return self.charging_info[car_id][Key.request_time]

    def get_pile_id(self, car_id):
        return self.charging_info[car_id][Key.pile_id]

    def get_bill_id(self, car_id):
        return self.charging_info[car_id][Key.additional_bill_id]

    def get_mode(self, car_id):
        return self.charging_info[car_id][Key.request_mode]

    def set_car_state(self, car_id, car_state):
        self.charging_info[car_id][Key.car_state] = car_state

    def set_queue_num(self, car_id, queue_num):
        self.charging_info[car_id][Key.queue_num] = queue_num

    def set_request_time(self, car_id, request_time):
        self.charging_info[car_id][Key.request_time] = request_time

    def set_pile_id(self, car_id, pile_id):
        self.charging_info[car_id][Key.pile_id] = pile_id

    def set_bill_id(self, car_id, bill_id):
        self.charging_info[car_id][Key.additional_bill_id] = bill_id

    def set_mode(self, car_id, mode):
        self.charging_info[car_id][Key.request_mode] = mode


charging_info = ChargingInfo()


class QInfo:
    def __init__(self, mode: str, user_id: int, car_id: str, degree: float, queue_num: str):
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
        self.queue_num = queue_num


class QInfoFactory:
    def __init__(self):
        self.__fast_number = 0
        self.__slow_number = 0

    def give_a_number(self, mode):
        if mode == "快充":
            self.__fast_number += 1
            number = "F" + str(self.__fast_number)
        else:
            self.__slow_number += 1
            number = "T" + str(self.__slow_number)
        return number

    def manufacture_q_info(self, mode: str, user_id: int, car_id: str, degree: float):
        return QInfo(mode, user_id, car_id, degree, self.give_a_number(mode))


q_info_factory = QInfoFactory()


class QQueue:
    def __init__(self, mode: str, max_len):
        self.mode = mode
        self.max_len = max_len
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


class ChargingStationQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode, max_len=config.ChargingQueueLen)

    def change_degree(self, index, degree):
        raise Exception("Can't change degree in charging area")


class ChargingStation:
    def __init__(self, mode: str, pile_id: int):
        self.mode = mode
        self.pile_id = pile_id
        if mode == "快充":
            self.speed = 30.0
        else:
            self.speed = 7.0
        self.q_queue = ChargingStationQueue(mode)
        self.end_time: Optional[float] = None
        self.state: PileState = PileState.free
        self.timer: Optional[VirtualTimer] = None

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
            self.timer = my_time.start_timer(first_info.during, callback=dispatch.a_car_finish,
                                             args=(self.pile_id, self.mode, car_id))
        else:
            raise Exception("You are not the first one in the charging queue, can not start charging")

    # 由用户或系统发起
    def end_charging(self, car_id):
        """
        分3种情况调用:
        ① 由系统定时器结束充电发起。 ② 由用户终止充电。 ③ 用户还没有开始充电时取消充电。
        :param car_id: car_id
        :return: None
        """
        # 检查是否是正确的操作
        first_info = self.q_queue.get_first_one()
        # 如果他不是第一位, 或是第一位但充电桩不在充电
        if (first_info.car_id != car_id) or (first_info.car_id == car_id and self.state == PileState.free):
            # ③取消充电
            position = self.q_queue.get_car_position(car_id)
            self.q_queue.pop(position)
            return
        # ①②结束充电
        if self.state != PileState.using:
            raise Exception("Pile is not charging, can not end charging")
        # 结束定时器
        self.timer.terminate()
        # 改变充电桩状态
        self.state = PileState.free
        # 出队列
        self.q_queue.pop()
        # 更改预计排队时间
        if self.q_queue.get_len() == 0:
            self.end_time = None

    def get_end_time(self):
        return self.end_time

    def has_vacancy(self):
        return self.q_queue.get_len() < self.q_queue.max_len


class ChargingAreaFastOrSlow:
    def __init__(self, mode):
        self.mode = mode
        if mode == "快充":
            self.pile_num = config.FastChargingPileNum
            keys = [i * 10 + 0 for i in range(1, config.FastChargingPileNum + 1)]
        else:
            self.pile_num = config.TrickleChargingPileNum
            keys = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]
        values = [ChargingStation(mode, i) for i in keys]
        self.pile_dict = dict(zip(keys, values))

    def has_vacancy(self):
        for station in self.pile_dict.values():
            if station.has_vacancy():
                return True
        return False

    def add_car(self, pile_id, q_info: QInfo):
        return self.pile_dict[pile_id].add_car(q_info)

    def end_charging(self, car_id):
        pile_id = charging_info.get_pile_id(car_id)
        self.pile_dict[pile_id].end_charging(car_id)

    def dispatch(self):
        """
        选出所有充电桩中预计完成充电时间最短的的充电桩。
        由于如果充电桩队列为空，预计时间为-1，所以可以直接通过比得到取最小值得出。
        如果有预计结束时间重复的充电桩，只会给出其中一个充电桩的编号。
        :return: 充电桩编号
        """
        end_time_dict = dict(
            [(pile.get_end_time(), pile.pile_id) for pile in self.pile_dict.values() if pile.has_vacancy()])
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

    def end_charging(self, car_id):
        mode = charging_info.get_mode(car_id)
        if mode == "快充":
            self.fast_area.end_charging(car_id)
        else:
            self.slow_area.end_charging(car_id)

    def get_your_position(self, car_id):
        mode = charging_info.get_mode(car_id)
        pile_id = charging_info.get_pile_id(car_id)
        if mode == "快充":
            self.fast_area.pile_dict[pile_id].q_queue.get_car_position(car_id)
        else:
            self.slow_area.pile_dict[pile_id].q_queue.get_car_position(car_id)


class WaitingQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode, config.WaitingAreaSize)


class WaitingArea:
    def __init__(self):
        self.fast_queue = WaitingQueue("快充")
        self.slow_queue = WaitingQueue("慢充")
        self.max_len = config.WaitingAreaSize

    def get_all_len(self):
        return self.fast_queue.get_len() + self.slow_queue.get_len()

    def add_car(self, q_info: QInfo):
        if self.get_all_len() >= self.max_len:
            raise Exception("Could not add car into waiting area")
        if q_info.mode == "快充":
            self.fast_queue.push(q_info)
        else:
            self.slow_queue.push(q_info)

    def has_vacancy(self):
        return self.get_all_len() < self.max_len

    def has_car(self, mode):
        if mode == "快充":
            return self.fast_queue.get_len() != 0
        else:
            return self.slow_queue.get_len() != 0

    def call_out(self, mode) -> QInfo:
        if mode == "快充":
            return self.fast_queue.pop()
        else:
            return self.slow_queue.pop()

    def get_first(self, mode):
        if mode == "快充":
            return self.fast_queue.get_first_one()
        else:
            return self.slow_queue.get_first_one()

    def get_queue_len(self, mode):
        if mode == "快充":
            return self.fast_queue.get_len()
        else:
            return self.fast_queue.get_len()

    def get_car_position(self, car_id):
        mode = charging_info.get_mode(car_id)
        if mode == "快充":
            return self.fast_queue.get_car_position(car_id)
        else:
            return self.slow_queue.get_car_position(car_id)

    def change_degree(self, car_id, new_degree):
        mode = charging_info.get_mode(car_id)
        position: int = self.get_car_position(car_id)
        if mode == "快充":
            self.fast_queue.change_degree(position, new_degree)
        else:
            self.slow_queue.change_degree(position, new_degree)

    def cancel_waiting(self, car_id):
        mode = charging_info.get_mode(car_id)
        position: int = self.get_car_position(car_id)
        if mode == "快充":
            return self.fast_queue.pop(position)
        else:
            return self.slow_queue.pop(position)

    def change_mode(self, car_id, new_mode):
        mode = charging_info.get_mode(car_id)
        if mode == new_mode:
            raise Exception("Mode is same")
        q_info = self.cancel_waiting(car_id)
        q_info.mode = new_mode
        # 重新派号
        q_info.queue_num = q_info_factory.give_a_number(mode)
        self.add_car(q_info)


class AllArea:
    def __init__(self):
        self.charging_area = ChargingArea()
        self.waiting_area = WaitingArea()

    def waiting_area_add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)

    def charging_is_vacancy(self, mode):
        is_vacancy = self.charging_area.has_vacancy(mode)
        return is_vacancy
