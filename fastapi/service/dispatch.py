from domain.user import AllArea, all_area, ChargingInfo, charging_info, QInfoFactory, q_info_factory, UserState
# from domain.user import *
# from domain import user
from utils.my_time import virtual_time


class Dispatch:
    def __init__(self):
        self.area: AllArea = all_area
        self.info: ChargingInfo = charging_info
        self.q_info_factory: QInfoFactory = q_info_factory
        print(self.info, self.q_info_factory)

    def get_car_state(self, car_id):
        car_state = self.info.get_car_state(car_id)
        car_position = None
        queue_num = None
        request_time = None
        pile_id = None
        if car_state == UserState.free:
            car_state = UserState.free.value
        elif car_state == UserState.waiting:
            car_state = UserState.waiting.value
            car_position = self.area.waiting_area.get_car_position(car_id)
            queue_num = self.info.get_queue_num(car_id)
            request_time = self.info.get_request_time(car_id)
        else:
            car_state = UserState.waiting_for_charging.value
            car_position = self.area.charging_area.get_your_position(car_id)
            queue_num = self.info.get_queue_num(car_id)
            request_time = self.info.get_request_time(car_id)
            pile_id = self.info.get_pile_id(car_id)
        return {
            "code": 1,
            "message": "请求成功",
            "data": {
                "car_state": car_state,
                "car_position": car_position,
                "queue_num": queue_num,
                "request_time": request_time,
                "pile_id": pile_id
            }
        }

    def new_car_come(self, user_id, car_id, mode, degree):
        q_info = self.q_info_factory.manufacture_q_info(mode=mode, user_id=user_id, car_id=car_id, degree=degree)
        # 先查看等候区是否有空位
        if not self.area.waiting_area.has_vacancy():
            # 如果没有空位就直接返回失败信息
            return {"code": 0, "message": "等候区已满"}
        # 加入
        self.info.add_car(car_id)
        # 查看对应的模式的充电桩是否有空位
        if self.area.charging_area.has_vacancy(mode):
            # 如果有，寻找一个存在空位且等待时间最短的充电桩
            pile_id = self.area.charging_area.dispatch(mode)
            # 把车直接加入充电桩队列,返回用户是否可以充电
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            # 改变用户状态
            self.info.set_car_state(car_id, user_state)
            car_position = self.area.charging_area.get_your_position(car_id)
        else:
            # 加入等候区
            self.area.waiting_area.add_car(q_info)
            # 改变用户状态
            self.info.set_car_state(car_id, UserState.waiting)
            car_position = self.area.waiting_area.get_car_position(car_id)
        return {
            "code": 1,
            "message": "请求成功",
            "data": {
                "car_position": car_position,
                "car_state": self.info.get_car_state(car_id).value,
                "queue_num": self.info.get_queue_num(car_id),
                "request_time": self.info.get_request_time(car_id)
            }
        }

    def __call_out(self, pile_id, mode):
        # 如果有等候区有匹配模式待叫号的车辆
        if self.area.waiting_area.has_car(mode):
            # 获取到最先的用户,并出队列
            q_info = self.area.waiting_area.call_out(mode)
            # 放入充电桩队列
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            # 改变用户状态
            self.info.set_car_state(q_info.car_id, user_state)

    def a_car_finish(self, pile_id, mode, car_id):
        # 由充电桩发起
        # 改变用户状态
        self.info.set_car_state(car_id, UserState.end)
        # 调用充电桩的自动结束充电接口
        self.area.charging_area.end_charging(car_id)
        # 叫号
        self.__call_out(pile_id, mode)

    def user_terminate(self, car_id):  # 和取消充电合并
        # 用户在不同区做不同处理
        state = self.info.get_car_state(car_id)
        if state == UserState.end:
            return {"code": 0, "message": "充电已结束"}
        elif state == UserState.charging:
            # 结束充电
            self.area.charging_area.end_charging(car_id)  # 线程是安全的，因为如果是定时器线程结束充电，会先改变用户状态
            # 改变用户状态
            self.info.set_car_state(car_id, UserState.end)
            # 叫号
            pile_id = self.info.get_pile_id(car_id)
            mode = self.info.get_mode(car_id)
            self.__call_out(pile_id, mode)
            return {"code": 1, "message": "成功结束充电"}
        elif state == UserState.waiting:
            # 取消充电
            self.area.waiting_area.cancel_waiting(car_id)
            # 改变用户状态
            self.info.del_car(car_id)
            return {"code": 1, "message": "成功取消充电"}
        elif state == UserState.waiting_for_charging:
            # 取消充电
            self.area.charging_area.end_charging(car_id)
            # 改变用户状态
            self.info.del_car(car_id)
            return {"code": 1, "message": "成功取消充电"}

    def change_degree(self, car_id, degree):
        state = self.info.get_car_state(car_id)
        if state != UserState.waiting:
            return {"code": 0, "message": "用户不在等候区，无法修改充电量"}
        self.area.waiting_area.change_degree(car_id, degree)
        return {"code": 1, "message": "请求成功"}

    def change_mode(self, car_id, mode):
        state = self.info.get_car_state(car_id)
        if state != UserState.waiting:
            return {"code": 0, "message": "用户不在等候区，无法修改充模式"}
        old_mode = self.info.get_mode(car_id)
        if old_mode == mode:
            return {"code": 0, "message": "充电模式没有改变"}
        self.area.waiting_area.change_mode(car_id, mode)
        self.info.set_mode(car_id, mode)
        return {"code": 1, "message": "请求成功"}


dispatch = Dispatch()
