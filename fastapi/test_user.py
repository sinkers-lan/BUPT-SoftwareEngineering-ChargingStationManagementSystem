import datetime

import dao.user as user_dao
import dao.bill as bill_dao
from utils import utils
from utils.my_time import virtual_time


def logon():
    psw = utils.hash_password("1234")
    info = user_dao.logon("13911010126", psw, "京AB2431", 45.0)
    if info['code'] == 1:
        pass


def get_bill():
    virtual_time.start()
    data = bill_dao.get_bill(1)
    data["start_time"] = utils.formate_datetime_f(data["start_time"])
    data["end_time"] = utils.formate_datetime_f(data["end_time"])
    print(data)


if __name__ == "__main__":
    get_bill()
    pass
