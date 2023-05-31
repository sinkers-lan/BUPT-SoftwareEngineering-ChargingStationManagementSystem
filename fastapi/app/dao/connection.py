import sqlite3


class Connection:
    def __init__(self):
        """打开/创建数据库"""
        self.conn = sqlite3.connect('SoftwareEngineering.db')
        print("数据库打开成功")
        self.c = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        print("数据库关闭成功")
        self.conn.close()


my_connect = Connection()
