from domain.user import AllArea, QInfo, StateDict, UserState


class Dispatch:
    def __int__(self):
        self.area = AllArea()
        self.state_dict = StateDict()

    def new_car_come(self, user_id, car_id, mode, degree):
        q_info = QInfo(mode=mode, user_id=user_id, car_id=car_id, degree=degree)
        # 先查看等候区是否有空位
        if not self.area.waiting_area.has_vacancy():
            # 如果没有空位就直接返回失败信息
            return -1
        # 查看对应的模式的充电桩是否有空位
        if self.area.charging_area.has_vacancy(mode):
            # 如果有，寻找一个存在空位且等待时间最短的充电桩
            pile_id = self.area.charging_area.dispatch(mode)
            # 把车直接加入充电桩队列,返回用户是否可以充电
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            # 改变用户状态
            self.state_dict.change_car_state(car_id, state=user_state)
        else:
            # 加入等候区
            self.area.waiting_area.add_car(q_info)
            self.state_dict.change_car_state(car_id, state=UserState.waiting)

    def a_car_finish(self, pile_id, mode, car_id):
        # 由充电桩发起
        self.state_dict.change_car_state(car_id, state=UserState.end)
        # 如果有等候区有匹配模式待叫号的车辆
        if self.area.waiting_area.has_car(mode):
            # 获取到最先的用户,并出队列
            q_info = self.area.waiting_area.call_out(mode)
            # 放入充电桩队列
            user_state = self.area.charging_area.add_car(mode, pile_id, q_info)
            self.state_dict.change_car_state(q_info.car_id, state=user_state)

    def user_terminate(self, car_id):
        # 用户在不同区做不同处理
        state = self.state_dict.inquire_car_state(car_id)
        if state == UserState.end:
            return {"code": -1, "message": "充电已结束"}
        elif state == UserState.charging:
            # 需要通过car_id找到mode和pile_name
            self.area.charging_area


dispatch = Dispatch()
