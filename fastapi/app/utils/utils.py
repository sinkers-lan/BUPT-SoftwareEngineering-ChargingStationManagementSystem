# 用于生成token
import time

import jwt
import datetime
import hashlib
from app.utils import config


def generate_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload=payload, key="hello_my_teammates", algorithm='HS256')
    return token


def decode_token(token):
    if token is None:
        return False, "token为空"
    try:
        data = jwt.decode(token, key="hello_my_teammates", algorithms='HS256')
    except jwt.exceptions.InvalidTokenError:
        print("token解析失败")
        return False, "token解析失败"
    exp = data.pop('exp')
    if time.time() > exp:
        print('token已失效')
        return False, 'token已失效，请重新登录'
    return True, data.pop('user_id')


def hash_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    str_md5 = md5.hexdigest()
    return str_md5


def generate_bill_ls(bill_id):
    code_qz = 'DD'
    code_sj = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return code_qz + code_sj + str(bill_id).zfill(4)


def format_datetime_f(time_stamp: float):
    return datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]


def format_datetime_s(time_stamp: float):
    return datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S")


def format_date_to_timestamp(date: str):
    return time.mktime(time.strptime(date, "%Y-%m-%d"))


def calculate_bill(start_time: float, charge_duration: float, power: float):
    """

    :param power: 充电功率，单位为kW/h
    :param start_time: 开始计费的时间，单位为秒的浮点数
    :param charge_duration: 充电时长，单位为秒的浮点数
    :return:
    """
    peak_rate = config.PeakRate
    off_peak_rate = config.OffPeakRate
    normal_rate = config.NormalRate
    peak_time = [10, 11, 12, 13, 14, 18, 19, 20]
    off_peak_time = [23, 0, 1, 2, 3, 4, 5, 6]
    charge_power = power
    degree = charge_duration * charge_power / 3600
    service_fee = degree * config.ServiceFeeRate
    charge_fee = 0.0
    # 首先，计算从开始时间到整点的费用
    # 先将start_time转化为datetime
    start_datetime = datetime.datetime.fromtimestamp(start_time)
    # 然后取出整点的时间
    start_hour = start_datetime.hour
    # 然后，计算出结束时间的整点
    end_datetime = datetime.datetime.fromtimestamp(start_time + charge_duration)
    # 结束整点
    end_hour = end_datetime.hour
    # 如果开始整点和结束整点相同
    if start_hour == end_hour:
        # 如果开始时间属于高峰时间
        if start_hour in peak_time:
            charge_fee += charge_duration * peak_rate * charge_power / 3600
        # 如果开始时间属于低谷时间
        elif start_hour in off_peak_time:
            charge_fee += charge_duration * off_peak_rate * charge_power / 3600
        # 如果开始时间属于平常时间
        else:
            charge_fee += charge_duration * normal_rate * charge_power / 3600
        return round(charge_fee, 2), round(service_fee, 2)
    # 如果开始时间属于高峰时间
    if start_hour in peak_time:
        charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) \
                      * peak_rate * charge_power / 3600
    # 如果开始时间属于低谷时间
    elif start_hour in off_peak_time:
        charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) \
                      * off_peak_rate * charge_power / 3600
    # 如果开始时间属于平常时间
    else:
        charge_fee += (3600 - start_datetime.minute * 60 - start_datetime.second) \
                      * normal_rate * charge_power / 3600
    # 计算出从开始时间的整点到结束时间的整点的费用
    for i in range(start_hour + 1, end_hour):
        if i % 24 in peak_time:
            charge_fee += peak_rate * charge_power
        elif i % 24 in off_peak_time:
            charge_fee += off_peak_rate * charge_power
        else:
            charge_fee += normal_rate * charge_power
    # 最后，计算从整点到结束时间的费用
    # 如果结束时间属于高峰时间
    if end_hour % 24 in peak_time:
        charge_fee += (end_datetime.minute * 60 + end_datetime.second) * peak_rate * charge_power / 3600
    # 如果结束时间属于低谷时间
    elif end_hour % 24 in off_peak_time:
        charge_fee += (end_datetime.minute * 60 + end_datetime.second) * off_peak_rate * charge_power / 3600
    # 如果结束时间属于平常时间
    else:
        charge_fee += (end_datetime.minute * 60 + end_datetime.second) * normal_rate * charge_power / 3600
    return round(charge_fee, 2), round(service_fee, 2)


