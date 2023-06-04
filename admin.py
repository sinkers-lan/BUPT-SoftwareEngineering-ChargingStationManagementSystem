import sqlite3
from app.utils.my_time import virtual_time
from datetime import datetime
from datetime import date
from app.dao.connection import my_connect

# TODO: 充电桩四个工作状态：关闭 空闲 损坏 使用中
# 1.创建数据库连接
"""
如果connect()内的数据库名称存在，则与此数据库建立连接；
如果connect()内的数据库名称不存在，则新建数据库，再建立连接
"""
conn = my_connect.conn
# 2.创建cursor对象
cursor = my_connect.c

# 创建pile_state 表格
sql = """CREATE TABLE pile_state(
            pile_id Integer PRIMARY KEY autoincrement,
            workingState STRING NOT NULL,
            totalChargeNum INTEGER NOT NULL,
            totalChargeTime DOUBLE NOT NULL,
            totalCapacity DOUBLE NOT NULL
            );"""
# 执行SQL指令
# cursor.execute(sql)
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


# 执行SQL指令
# cursor.execute(sql)
# print("pile_report表格创建成功")


# TAG初始化
# 初始化pile_state表格里的充电桩
def init_pile_state(pile_id):
    result = cursor.execute(
        """
        select * from pile_state where pile_id=={}
        """.format(pile_id)
    )
    result = result.fetchall()
    # print(result)
    # 没有在表中查找到相应的pile_id
    if len(result) == 0:
        cursor.execute("""
        INSERT INTO pile_state(pile_id,workingState,totalChargeNum,totalChargeTime,totalCapacity) 
        VALUES({}, '空闲',0,0.0,0.0)
        """.format(pile_id))
        conn.commit()
        print("pile_id:{}初始化成功".format(pile_id))


# 查看充电桩状态
def getPileState(pile_id):
    flag = updatePileState(pile_id, cursor, conn)
    result = cursor.execute('select * from pile_state where pile_id=={}'.format(pile_id))
    result = result.fetchall()
    if len(result):
        seq = ('workingState', 'totalChargeNum', 'totalChargeTime', 'totalCapacity', 'charge_mode')
        data = dict.fromkeys(seq)
        for i in range(0, 4):
            data[seq[i]] = result[0][i + 1]
        if pile_id % 10:
            data['charge_mode'] = 'T'
        else:
            data['charge_mode'] = 'F'
        return data
    else:
        print("ERROR:can't get pile id{}'s state".format(pile_id))
        return None


def get_pile_state(pile_id):
    """根据pile_id返回充电桩状态"""
    cursor = my_connect.c.execute("select workingState from pile_state where pile_id=={}".format(pile_id))
    for row in cursor:
        return row[0]
    raise Exception("pile_id not exist")


# TAG
# 查看充电桩工作状态
def getPileWorkingState(pile_id, cursor):
    result = cursor.execute("select * from pile_state where pile_id={}".format(pile_id))
    result = result.fetchall
    if len(result):
        return result[0][1]
    else:
        print("ERROR:can't get pile_id:{}'s workingState".format(pile_id))


# 改变充电桩工作状态
# 成功返回1，失败返回0
def changePileState(pile_id, workingState):
    result = cursor.execute('select * from pile_state where pile_id=={}'.format(pile_id))
    result = result.fetchall()
    if len(result):
        cursor.execute("update pile_state set workingState = '{}' where pile_id={}".format(workingState, pile_id))
        conn.commit()
        return 1
    else:
        print("ERROR:can't change pile_id {} workingState".format(pile_id))
        return 0


# 在查询pilestate的数据时将其更新
# 通过求一次pile_report的sum，不用每次变动都更新pilestate数据库数据
def updatePileState(pile_id, cursor, conn):
    # TAG获取年月日的字符串
    # now=virtual_time.get_current_date()
    # date_format = "%Y-%m-%d"
    # now = datetime.strptime(date, date_format).date()
    now = date.fromtimestamp(virtual_time.get_current_time())
    # now = datetime.today()
    result = cursor.execute(
        "select sum(total_charge_num),sum(total_charge_time),sum(total_capacity) from pile_report where pile_id=={} and date<='{}'".format(
            pile_id, now))
    result = result.fetchall()
    if result[0][0]:
        cursor.execute('update pile_state set totalChargeNum={} where pile_id={}'.format(str(result[0][0]), pile_id))
        cursor.execute('update pile_state set totalChargeTime={} where pile_id={}'.format(str(result[0][1]), pile_id))
        cursor.execute('update pile_state set totalCapacity={} where pile_id={}'.format(str(result[0][2]), pile_id))
        conn.commit()
        return 1
    else:
        print("WARNING:don't exist pile_id={} ,update error".format(pile_id))
        return 0


# 初始化pile_report表格里的充电桩
def init_pile_report(pile_id, cursor, conn):
    # TAG获取年月日的字符串
    # date=virtual_time.get_current_date()
    # date='2023-06-01'
    # date_format = "%Y-%m-%d"
    # now=datetime.strptime(date,date_format).date()
    # now = date.today()
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
def updatePileReport(pile_id, chargeTime, capacity, chargeFee, serviceFee, cursor, conn):
    # TAG获取年月日的字符串
    # now=virtual_time.get_current_date()
    # date='2023-06-02'
    # date_format = "%Y-%m-%d"
    # now=datetime.strptime(date,date_format).date()
    # now = date.today()
    now = date.fromtimestamp(virtual_time.get_current_time())
    result = cursor.execute("select * from pile_report where pile_id=={} and date=='{}'".format(pile_id, now))
    result = result.fetchall()
    if len(result):
        cursor.execute(
            "update pile_report set total_charge_num={} where pile_id={} and date='{}'".format(str(result[0][2] + 1),
                                                                                               pile_id, now))
        cursor.execute("update pile_report set total_charge_time={} where pile_id={} and date='{}'".format(
            str(result[0][3] + chargeTime), pile_id, now))
        cursor.execute("update pile_report set total_capacity={} where pile_id={} and date='{}'".format(
            str(result[0][4] + capacity), pile_id, now))
        cursor.execute("update pile_report set total_charge_fee={} where pile_id={} and date='{}'".format(
            str(result[0][5] + chargeFee), pile_id, now))
        cursor.execute("update pile_report set total_service_fee={} where pile_id={} and date='{}'".format(
            str(result[0][6] + serviceFee), pile_id, now))
        conn.commit()
        return 1
    # TAG 没有当日的充电桩记录则进行初始化
    else:
        init_pile_report(pile_id, cursor, conn)
        print("WARING:Don't exist pile_id {},date {},so init pile".format(pile_id, now))
        updatePileReport(pile_id, chargeTime, capacity, chargeFee, serviceFee, cursor, conn)


# init_pile_state(10)
# init_pile_state(20)
# init_pile_state(31)
# init_pile_state(41)
# init_pile_state(51)
'''
# getPileState(20,cursor,conn)
updatePileReport(20,1.2,3.5,1.4,0.7,cursor,conn)
getPileState(20,cursor,conn)
updatePileReport(20,2.4,3,2,0.4,cursor,conn)
getPileState(20,cursor,conn)
date_format = "%Y-%m-%d"
getPileReport(20,datetime.strptime('2023-06-01',date_format).date(),datetime.strptime('2023-06-02',date_format).date(),cursor)
changePileState(10,'关闭',cursor,conn)
getPileState(10,cursor,conn)
changePileState(31,'损坏',cursor,conn)
getPileState(31,cursor,conn)
# 关闭数据库连接
conn.close()
'''
'''
updatePileReport(10,3.4,1.5,2.4,9.7,cursor,conn)
updatePileReport(10,2,9,3.4,5.3,cursor,conn)
updatePileReport(31,5.4,3.6,2,6,cursor,conn)
updatePileReport(41,1,1.6,5,8,cursor,conn)
updatePileReport(51,2,6.3,1,6,cursor,conn)'''
# init_pile_state(10, cursor, conn)
