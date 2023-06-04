import datetime

import app.dao.user as user_dao
import app.dao.bill as bill_dao
import app.dao.admin as admin_dao
from app.dao.connection import my_connect
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


def init_pile():
    cursor = my_connect.c
    conn = my_connect.conn
    admin_dao.init_pile_state(10, cursor, conn)
    admin_dao.init_pile_state(20, cursor, conn)
    admin_dao.init_pile_state(11, cursor, conn)
    admin_dao.init_pile_state(21, cursor, conn)
    admin_dao.init_pile_state(31, cursor, conn)

if __name__ == "__main__":
    init_pile()
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


    pass
