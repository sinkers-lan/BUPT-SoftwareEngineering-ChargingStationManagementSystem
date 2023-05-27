from domain.user import AllArea, QInfo, StateDict, UserState


class Dispatch:
    def __int__(self):
        self.area = AllArea()
        self.state_dict = StateDict()

    def new_car_come(self, user_id, car_id, mode, degree):
        q_info = QInfo(mode=mode, user_id=user_id, car_id=car_id, degree=degree)
        # 先查看等候区是否有空位
        if not self.area.waiting_area.has_vacancy():
            return
        # 先查看对应的模式是否有空位
        if self.area.charging_area.has_vacancy(mode):
            # 寻找一个等待时间最短的充电桩，返回是否可以直接充电
            # self.state_dict.change_car_state(car_id, state=UserState.waiting_for_charging)
            pass
        else:
            # 加入等候区
            self.area.waiting_area.add_car(q_info)
            self.state_dict.change_car_state(car_id, state=UserState.waiting)

    def a_car_finish(self, pile_id, mode, car_id):
        # 由充电桩发起
        self.state_dict.change_car_state(car_id, state=UserState.end)
        # 叫号
        if self.area.waiting_area.has_car():
            # 获取全部等候该模式的用户的预计充电时间
            time_list = self.area.waiting_area.get_time_list(mode)
            


