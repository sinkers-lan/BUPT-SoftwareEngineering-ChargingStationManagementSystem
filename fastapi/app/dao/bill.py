from typing import Optional

from app.utils import utils
from app.dao.connection import my_connect
from app.utils.my_time import virtual_time
import sqlite3


def bill_table():
    my_connect.c.execute('''CREATE TABLE bill
               (bill_id          Integer PRIMARY KEY autoincrement,
               bill_ls           TEXT,
               car_id            TEXT     NOT NULL,
               bill_date         TEXT    NOT NULL,
               pile_id           Integer    NOT NULL,
               charge_amount     REAL    NOT NULL,
               charge_duration     REAL    NOT NULL,
               start_time         REAL    NOT NULL,
               end_time         REAL    NOT NULL,
               total_charge_fee         REAL    NOT NULL,
               total_service_fee         REAL    NOT NULL,
               total_fee         REAL    NOT NULL,
               pay_state         Integer      NOT NULL);''')
    print("数据表创建成功")
    my_connect.conn.commit()


def create_bill(car_id: str, pile_id: int, charge_amount: float, charge_duration: float, total_charge_fee: float,
                total_service_fee: float):
    bill_date = virtual_time.get_current_date()
    start_time = virtual_time.get_current_time()
    end_time = start_time + charge_duration
    # print("when create bill, end_time is ", utils.formate_datetime_s(end_time))
    total_fee = total_charge_fee + total_service_fee
    my_connect.c.execute(f"INSERT INTO bill (car_id,bill_date,pile_id,charge_amount,charge_duration, \
    start_time,end_time,total_charge_fee,total_service_fee,total_fee,pay_state) \
    VALUES ('{car_id}', '{bill_date}', {pile_id}, {charge_amount}, {charge_duration}, \
    {start_time}, {end_time}, {total_charge_fee}, {total_service_fee}, {total_fee}, {0})")
    print("账单数据表插入成功")
    my_connect.conn.commit()
    cursor = my_connect.c.execute(f"select max(bill_id) from bill")
    if cursor.rowcount == 0:
        raise sqlite3.Error("bill_id is None")
    for row in cursor:
        bill_id = row[0]
    bill_ls = utils.generate_bill_ls(bill_id)
    my_connect.c.execute(f"UPDATE bill set bill_ls = '{bill_ls}' where bill_id={bill_id}")
    print("账单数据库表填入流水号成功")
    my_connect.conn.commit()
    return bill_ls


def get_bill_from_id(bill_id: int):
    """
    用于测试
    :param bill_id: 主键
    :return: 全部数据
    """
    cursor = my_connect.c.execute(f"select bill_ls,car_id,bill_date,pile_id,charge_amount,charge_duration, \
    start_time,end_time,total_charge_fee,total_service_fee,total_fee,pay_state from bill where bill_id={bill_id}")
    for row in cursor:
        return {
            "bill_id": row[0],
            "car_id": row[1],
            "bill_date": row[2],
            "pile_id": row[3],
            "charge_amount": round(row[4], 2),
            "charge_duration": round(row[5] / 3600, 2),
            "start_time": utils.format_datetime_s(row[6]),
            "end_time": utils.format_datetime_s(row[7]),
            "total_charge_fee": row[8],
            "total_service_fee": row[9],
            "total_fee": row[10],
            "pay_state": row[11],
        }


def get_bill(bill_ls, conn=my_connect.conn, c=my_connect.c):
    """bill_id,car_id,bill_date,pile_id,charge_amount,charge_duration, \
    start_time,end_time,total_charge_fee,total_service_fee,total_fee,pay_state"""
    cursor = c.execute(f"select bill_id,car_id,bill_date,pile_id,charge_amount,charge_duration, \
    start_time,end_time,total_charge_fee,total_service_fee,total_fee,pay_state from bill where bill_ls='{bill_ls}'")
    if cursor.rowcount == 0:
        raise Exception("bill_ls is not exist")
    for row in cursor:
        return {
            "bill_id": bill_ls,
            "car_id": row[1],
            "bill_date": row[2],
            "pile_id": row[3],
            "charge_amount": round(row[4], 2),
            "charge_duration": round(row[5] / 3600, 2),
            "start_time": utils.format_datetime_s(row[6]),
            "end_time": utils.format_datetime_s(row[7]),
            "total_charge_fee": row[8],
            "total_service_fee": row[9],
            "total_fee": row[10],
            "pay_state": row[11],
        }


def get_all_bill(car_id: str, date: Optional[str] = None):
    """如果没有传入日期，就返回所有的账单。如果bill_date==date，就返回当天的账单"""
    if date is None or date is "":
        cursor = my_connect.c.execute(f"select bill_ls,car_id,bill_date,pile_id, \
        start_time,end_time,total_fee,pay_state from bill where car_id='{car_id}'")
    else:
        cursor = my_connect.c.execute(f"select bill_ls,car_id,bill_date,pile_id, \
        start_time,end_time,total_fee,pay_state from bill where car_id='{car_id}' and bill_date='{date}'")
    result = []
    for row in cursor:
        result.append({
            "bill_id": row[0],
            "car_id": row[1],
            "bill_date": row[2],
            "pile_id": row[3],
            "start_time": utils.format_datetime_s(row[4]),
            "end_time": utils.format_datetime_s(row[5]),
            "total_fee": row[6],
            "pay_state": row[7],
        })
        # print(result)
    return result


def pay_the_bill(bill_ls: str):
    """支付账单, 将pay_state置为1。如果账单不存在，返回False。如果pay_state已经为1，返回False"""
    cursor = my_connect.c.execute(f"select pay_state from bill where bill_ls='{bill_ls}'")
    if cursor.rowcount == 0:
        return False, "账单不存在"
    for row in cursor:
        if row[0] == 1:
            return False, "账单已经支付"
    my_connect.c.execute(f"UPDATE bill set pay_state = 1 where bill_ls='{bill_ls}'")
    my_connect.conn.commit()
    return True, "支付成功"


def get_car_id(bill_ls: str):
    cursor = my_connect.c.execute(f"select car_id from bill where bill_ls='{bill_ls}'")
    if cursor.rowcount == 0:
        raise Exception("bill_ls not exist")
    for row in cursor:
        return row[0]


def update_bill(bill_ls: str, total_charge_fee: float, total_service_fee: float, end_time: float,
                charge_duration: float, charge_amount: float):
    total_fee = total_charge_fee + total_service_fee
    # print("when update bill, end_time is", utils.formate_datetime_f(end_time), utils.formate_datetime_s(end_time))
    my_connect.c.execute(f"UPDATE bill set total_charge_fee = {total_charge_fee},total_service_fee = {total_service_fee}, \
        total_fee = {total_fee},end_time = {end_time},charge_duration={charge_duration},charge_amount={charge_amount}\
         where bill_ls='{bill_ls}'")
    my_connect.conn.commit()


def get_start_time(bill_ls: str):
    cursor = my_connect.c.execute(f"select start_time from bill where bill_ls='{bill_ls}'")
    if cursor.rowcount == 0:
        raise Exception("bill_ls not exist")
    for row in cursor:
        return row[0]


def del_bill(bill_id: int):
    my_connect.c.execute(f"delete from bill where bill_id={bill_id}")
    my_connect.conn.commit()
