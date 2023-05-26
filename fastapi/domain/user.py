from typing import List


class QInfo:
    def __init__(self, mode: str, user_id: int, car_id: str, degree: float, start_time):
        self.mode = mode
        self.user_id = user_id
        self.car_id = car_id
        self.degree = degree
        self.start_time = start_time
        if mode == "快充":
            speed = 30.0
        else:
            speed = 7.0
        self.during = degree / speed


class QQueue:
    def __init__(self, mode: str, max_len):
        self.mode = mode
        self.len = 0
        self.max_len = max_len
        self.__q: List[QInfo] = []

    def get_your_len(self, car_id):
        i = 0
        for q_info in self.__q:
            if q_info.car_id == car_id:
                return i
            i += 1
        return -1

    def pop(self):
        if self.len == 0:
            print("pop error")
            return
        self.len -= 1
        return self.__q.pop()

    def push(self, q_info: QInfo):
        if self.len == self.max_len:
            print("push error")
            return
        self.len += 1
        self.__q.append(q_info)


class ChargingStationQueue(QQueue):
    def __init__(self, mode: str, name: str):
        super().__init__(mode, 2)


class ChargingStation:
    def __init__(self, mode, name):
        self.mode = mode
        self.name = name
        if mode == "快充":
            self.speed = 30.0
        else:
            self.speed = 7.0
        self.state = "空闲"
        self.q_queue = ChargingStationQueue(mode, name)

    def get_queue_len(self):
        return self.q_queue.len

    def add_car(self, q_info: QInfo):
        self.q_queue.push(q_info)



class WaitingQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode, 6)


class WaitingArea:
    def __init__(self):
        self.fast_queue = WaitingQueue("快充")
        self.slow_queue = WaitingQueue("慢充")
        self.max_len = 6
        self.all_len = 0

    def add_car(self, q_info: QInfo):
        # fast_len = self.fast_queue.len
        # slow_len = self.slow_queue.len
        if self.all_len >= self.max_len:
            return -1
        self.all_len += 1
        if q_info.mode == "快充":
            self.fast_queue.push(q_info)
            return self.fast_queue.len
        else:
            self.slow_queue.push(q_info)
            return self.slow_queue.len



class AllArea:
    def __init__(self):
        self.A = ChargingStation("快充", "A")
        self.B = ChargingStation("快充", "B")
        self.C = ChargingStation("慢充", "C")
        self.D = ChargingStation("慢充", "D")
        self.E = ChargingStation("慢充", "E")
        self.waiting_area = WaitingArea()
        self.q_infos: List[QInfo] = []


    # def inquire_car_state(self, car_id):

    def add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)
