import utils.utils
from dao.connection import my_connect
from utils.my_time import virtual_time
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
    end_time = start_time + charge_duration * 60 * 60
    total_fee = total_charge_fee + total_service_fee
    my_connect.c.execute(f"INSERT INTO bill (car_id,bill_date,pile_id,charge_amount,charge_duration, \
    start_time,end_time,total_charge_fee,total_service_fee,total_fee,pay_state) \
    VALUES ('{car_id}', '{bill_date}', {pile_id}, {charge_amount}, {charge_duration}, \
    {start_time}, {end_time}, {total_charge_fee}, {total_service_fee}, {total_fee}, {0})")
    print("数据表插入成功")
    my_connect.conn.commit()
    cursor = my_connect.c.execute(f"select max(bill_id) from bill")
    for row in cursor:
        bill_id = row[0]
    bill_ls = utils.utils.generate_bill_ls(bill_id)
    my_connect.c.execute(f"UPDATE bill set bill_ls = '{bill_ls}' where bill_id={bill_id}")
    print("数据库表修改成功")
    my_connect.conn.commit()


def get_bill(bill_id: int):
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
            "charge_amount": row[4],
            "charge_duration": row[5],
            "start_time": row[6],
            "end_time": row[7],
            "total_charge_fee": row[8],
            "total_service_fee": row[9],
            "total_fee": row[10],
            "pay_state": row[11],
        }
