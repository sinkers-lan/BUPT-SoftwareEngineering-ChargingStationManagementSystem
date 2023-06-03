import datetime

import app.dao.user as user_dao
import app.dao.bill as bill_dao
from app.utils import utils
from app.utils.my_time import virtual_time
from app.utils import config


def logon():
    psw = utils.hash_password("1234")
    info = user_dao.logon("13911010126", psw, "京AB2431", 45.0)
    if info['code'] == 1:
        pass


def get_bill():
    virtual_time.start()
    data = bill_dao.get_bill(1)
    data["start_time"] = utils.format_datetime_f(data["start_time"])
    data["end_time"] = utils.format_datetime_f(data["end_time"])
    print(data)


def del_bill(bill_id):
    bill_dao.del_bill(bill_id)


# def calculate_bill(start_time: float, charge_duration: float):
#     """
#
#     :param start_time: 开始计费的时间，单位为秒的浮点数
#     :param charge_duration: 充电时长，单位为秒的浮点数
#     :return: charge_fee, service_fee
#     """
#     peak_rate = config.PeakRate
#     off_peak_rate = config.OffPeakRate
#     normal_rate = config.NormalRate
#     peak_time = [10, 11, 12, 13, 14, 18, 19, 20]
#     off_peak_time = [23, 0, 1, 2, 3, 4, 5, 6]
#     charge_power = 30.0
#     degree = charge_duration * charge_power / 3600
#     service_fee = degree * config.ServiceFeeRate
#     charge_fee = 0.0
#     # 首先，计算从开始时间到整点的费用
#     # 先将start_time转化为datetime
#     start_datetime = datetime.datetime.fromtimestamp(start_time)
#     # 然后取出整点的时间
#     start_hour = start_datetime.hour
#     # 然后，计算出结束时间的整点
#     end_datetime = datetime.datetime.fromtimestamp(start_time + charge_duration)
#     # 结束整点
#     end_hour = end_datetime.hour
#     # 如果开始整点和结束整点相同
#     if start_hour == end_hour:
#         # 如果开始时间属于高峰时间
#         if start_hour in peak_time:
#             charge_fee += charge_duration * peak_rate * charge_power / 3600
#         # 如果开始时间属于低谷时间
#         elif start_hour in off_peak_time:
#             charge_fee += charge_duration * off_peak_rate * charge_power / 3600
#         # 如果开始时间属于平常时间
#         else:
#             charge_fee += charge_duration * normal_rate * charge_power / 3600
#         return (charge_fee, 2), round(service_fee, 2)
#     # 如果开始时间属于高峰时间
#     if start_hour in peak_time:
#         charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) * peak_rate * charge_power / 3600
#     # 如果开始时间属于低谷时间
#     elif start_hour in off_peak_time:
#         charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) * off_peak_rate * charge_power / 3600
#     # 如果开始时间属于平常时间
#     else:
#         charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) * normal_rate * charge_power / 3600
#     # 计算出从开始时间的整点到结束时间的整点的费用
#     for i in range(start_hour + 1, end_hour):
#         if i % 24 in peak_time:
#             charge_fee += peak_rate * charge_power
#         elif i % 24 in off_peak_time:
#             charge_fee += off_peak_rate * charge_power
#         else:
#             charge_fee += normal_rate * charge_power
#     # 最后，计算从整点到结束时间的费用
#     # 如果结束时间属于高峰时间
#     if end_hour % 24 in peak_time:
#         charge_fee += (end_datetime.minute * 60 + end_datetime.second) * peak_rate * charge_power / 3600
#     # 如果结束时间属于低谷时间
#     elif end_hour % 24 in off_peak_time:
#         charge_fee += (end_datetime.minute * 60 + end_datetime.second) * off_peak_rate * charge_power / 3600
#     # 如果结束时间属于平常时间
#     else:
#         charge_fee += (end_datetime.minute * 60 + end_datetime.second) * normal_rate * charge_power / 3600
#     return round(charge_fee, 2), round(service_fee, 2)


if __name__ == "__main__":
    # start_time = datetime.datetime.now()
    # during = 60
    # """
    # 充电60s=1min，充电功率为30kW，充电量为0.5度
    # 峰时费率为1.0，则峰时费用为0.5元
    # """
    # during = 3665
    # """
    # 充电1h，充电功率为30kW，充电量为30度
    # 峰时费率为1.0，则峰时费用为30元
    # """
    # charge_fee, service_fee = calculate_bill(start_time.timestamp(), during)
    # print(charge_fee, service_fee)

    del_bill(1)
    pass
