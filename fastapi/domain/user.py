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
    def __init__(self, mode: str):
        self.mode = mode
        self.len = 0
        self.q: List[QInfo] = []

    def get_your_len(self, car_id):
        i = 0
        for q_info in self.q:
            if q_info.car_id == car_id:
                return i
            i += 1
        return -1

    def pop(self):
        self.len -= 1
        return self.q.pop()

    def push(self, q_info: QInfo):
        self.len += 1
        self.q.append(q_info)


class ChargingStationQueue(QQueue):
    def __init__(self, mode: str, ref: str):
        super().__init__(mode)
        self.ref = ref
        if mode == "快充":
            self.speed = 30.0
        else:
            self.speed = 7.0


class WaitingQueue(QQueue):
    def __init__(self, mode: str):
        super().__init__(mode)


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

    # def inquire_car_state(self, ):
