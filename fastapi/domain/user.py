from typing import List, Optional


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
            return -1
        self.len -= 1
        return self.__q.pop()

    def push(self, q_info: QInfo):
        if self.len == self.max_len:
            print("push error")
            return -1
        self.len += 1
        self.__q.append(q_info)


class ChargingStationQueue(QQueue):
    def __init__(self, mode: str, name: str):
        super().__init__(mode, max_len=2)


class ChargingStation:
    def __init__(self, mode: str, name: str):
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


class ChargingAreaFastOrSlow:
    def __init__(self, mode):
        self.mode = mode
        if mode == "快充":
            self.charging_station_num = 2
            self.charging_stations = [
                ChargingStation(mode, "A"),
                ChargingStation(mode, "B")
            ]
        else:
            self.charging_station_num = 3
            self.charging_stations = [
                ChargingStation(mode, "C"),
                ChargingStation(mode, "D"),
                ChargingStation(mode, "E")
            ]

    def has_vacancy(self):
        for station in self.charging_stations:
            if station.get_queue_len() < 2:
                return True, station.name
        return False, None


class ChargingAreal:
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
        self.charging_area = ChargingAreal()
        self.waiting_area = WaitingArea()
        self.q_infos: List[QInfo] = []

    # def inquire_car_state(self, car_id):

    def waiting_area_add_car(self, q_info: QInfo):
        self.waiting_area.add_car(q_info)

    def charging_is_vacancy(self, mode):
        is_vacancy, pile_name = self.charging_area.has_vacancy(mode)

    def
