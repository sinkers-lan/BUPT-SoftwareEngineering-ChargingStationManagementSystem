import sqlite3
from app.utils.my_time import virtual_time
from datetime import datetime
from datetime import date
from app.dao.connection import my_connect
import app.utils.config as config

# TODO: 充电桩四个工作状态：关闭 空闲 损坏 使用中
# 1.创建数据库连接
"""
如果connect()内的数据库名称存在，则与此数据库建立连接；
如果connect()内的数据库名称不存在，则新建数据库，再建立连接
"""

my_conn = my_connect.conn
my_cursor = my_connect.c
# 快充充电桩数量
fast_pile_id = [i * 10 + 0 for i in range(1, config.FastChargingPileNum + 1)]
# 慢充充电桩数量
slow_pile_id = [i * 10 + 1 for i in range(1, config.TrickleChargingPileNum + 1)]

total_pile_id = fast_pile_id + slow_pile_id
# 初始化充电桩状态
pileState = {key: '空闲' for key in total_pile_id}
# print(pileState)
# 创建pile_state 表格
sql = """CREATE TABLE pile_state(
            pile_id Integer PRIMARY KEY autoincrement,
            workingState STRING NOT NULL,
            totalChargeNum INTEGER NOT NULL,
            totalChargeTime DOUBLE NOT NULL,
            totalCapacity DOUBLE NOT NULL
            );"""
# 执行SQL指令
# my_cursor.execute(sql)
# print("pile_state表格创建成功")

# 创建pile_report表格
sql = """CREATE TABLE pile_report(
            pile_id Integer,
            date DATE NOT NULL,
            total_charge_num INTEGER NOT NULL,
            total_charge_time DOUBLE NOT NULL,
            total_capacity DOUBLE NOT NULL,
            total_charge_fee DOUBLE NOT NULL,
            total_service_fee DOUBLE NOT NULL,
            primary key (pile_id,date)
            );"""


# 查看充电桩状态
def getPileState(pile_id):
    if pile_id in total_pile_id:
        now = date.fromtimestamp(virtual_time.get_current_time())
        result = my_cursor.execute(
            "select sum(total_charge_num),sum(total_charge_time),sum(total_capacity) from pile_report where pile_id=={} and date<='{}'".format(
                pile_id, now))
        result = result.fetchall()
        seq = ('workingState', 'totalChargeNum', 'totalChargeTime', 'totalCapacity', 'charge_mode')
        data = dict.fromkeys(seq)
        data['workingState'] = pileState[pile_id]
        if result[0][0]:
            for i in range(1, 4):
                data[seq[i]] = result[0][i - 1]
        else:
            data['totalChargeNum'] = 0
            data['totalChargeTime'] = 0.0
            data['totalCapacity'] = 0.0
        if pile_id % 10:
            data['charge_mode'] = 'T'
        else:
            data['charge_mode'] = 'F'
        print(data)
        return data
    else:
        print(f"ERROR:pile {pile_id} doesn't exist")
        return None


def get_pile_state(pile_id):
    """根据pile_id返回充电桩状态"""
    if pile_id in total_pile_id:
        return pileState[pile_id]
    else:
        print(f"ERROR:pile {pile_id} doesn't exist")
        return None


# 改变充电桩工作状态
# 成功返回1，失败返回0
def changePileState(pile_id, workingState):
    if pile_id in total_pile_id:
        pileState[pile_id] = workingState
        return 1
    else:
        print(f"ERROR:pile {pile_id} doesn't exist")
        return 0


# 初始化pile_report表格里的充电桩
def init_pile_report(pile_id, cursor, conn):
    now = date.fromtimestamp(virtual_time.get_current_time())
    result = cursor.execute(
        """
        select * from pile_report where pile_id=={} and date=={}
        """.format(pile_id, now)
    )
    result = result.fetchall()
    # 没有在表中查找到相应的pile_id和日期
    if len(result) == 0:
        cursor.execute("""
        INSERT INTO pile_report(pile_id,date,total_charge_num,total_charge_time,total_capacity,total_charge_fee,total_service_fee) 
        VALUES({}, '{}',0,0.0,0.0,0.0,0.0)
        """.format(pile_id, now))
        conn.commit()
    else:
        print("ERROR:init pile_state table error ,{} already exists".format(pile_id))


# 查看充电桩一段时间内的报表数据
def getPileReport(pile_id, start_date, end_date, cursor):
    result = cursor.execute(
        "SELECT SUM(total_charge_num), SUM(total_charge_time), SUM(total_capacity), SUM(total_charge_fee), SUM(total_service_fee) FROM pile_report WHERE pile_id = {} AND date >= '{}' AND date <= '{}'"
        .format(pile_id, start_date, end_date))
    result = result.fetchall()
    if result[0][0]:
        seq = (
            'total_charge_num', 'total_charge_time', 'total_capacity', 'total_charge_fee', 'total_service_fee',
            'total_fee',
            'start_date', 'end_date')
        data = dict.fromkeys(seq)
        for i in range(0, 5):
            data[seq[i]] = result[0][i]
        data['total_fee'] = data['total_charge_fee'] + data['total_service_fee']
        data['start_date'] = start_date
        data['end_date'] = end_date
        # print(data)
        return data
    else:
        print("ERROR:can't get pile {}'s report between {} and {}".format(pile_id, start_date, end_date))
        return {
            'total_charge_num': 0,
            'total_charge_time': 0.0,
            'total_capacity': 0.0,
            'total_charge_fee': 0.0,
            'total_service_fee': 0.0,
            'total_fee': 0.0,
            'start_date': start_date,
            'end_date': end_date
        }


# TAG:充电后调用一次
# 充电一次后，更新充电桩在pile_report的数据
# 成功返回1
def updatePileReport(pile_id: int, chargeTime: float, capacity: float, chargeFee: float, serviceFee: float,
                     conn=my_conn, c=my_cursor):
    # TAG获取年月日的字符串
    now = date.fromtimestamp(virtual_time.get_current_time())
    result = c.execute("select * from pile_report where pile_id=={} and date=='{}'".format(pile_id, now))
    result = result.fetchall()
    if len(result):
        # 更新pile_report表中的total_charge_num,total_charge_time,total_capacity,total_charge_fee,total_service_fee
        c.execute(f"update pile_report set total_charge_num=total_charge_num+1 \
        ,total_charge_time=total_charge_time+{chargeTime} \
        ,total_capacity=total_capacity+{capacity} \
        ,total_charge_fee=total_charge_fee+{chargeFee} \
        ,total_service_fee=total_service_fee+{serviceFee} \
        where pile_id={pile_id} and date='{now}'")
        conn.commit()
        return 1
    # TAG 没有当日的充电桩记录则进行初始化
    else:
        init_pile_report(pile_id, c, conn)
        print("WARING:Don't exist pile_id {},date {},so init pile".format(pile_id, now))
        updatePileReport(pile_id, chargeTime, capacity, chargeFee, serviceFee, conn, c)
