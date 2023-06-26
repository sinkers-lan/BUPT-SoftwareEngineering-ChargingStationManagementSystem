import sqlite3


class Connection:
    def __init__(self):
        """打开/创建数据库"""
        self.conn = sqlite3.connect('SoftwareEngineering.db', check_same_thread=False)
        print("数据库打开成功")
        self.c = self.conn.cursor()
        self.create_bill_table()
        self.create_user_table()
        self.create_pile_table()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        print("数据库关闭成功")
        self.conn.close()

    def create_bill_table(self):
        # 检查表是否存在
        self.c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='bill' ''')
        for row in self.c:
            if row[0] == 1:
                print("bill数据表已存在")
                return
        self.c.execute('''CREATE TABLE bill
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
        print("bill数据表创建成功")
        self.conn.commit()

    def create_user_table(self):
        # 检查表是否存在
        cursor = self.c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='user'")
        for row in cursor:
            if row[0] == 1:
                print("user数据表已存在")
                return
        self.c.execute('''CREATE TABLE user
                       (user_id             Integer PRIMARY KEY autoincrement,
                       user_name           TEXT     NOT NULL,
                       hash_password       TEXT     NOT NULL,
                       car_id             TEXT     NOT NULL,
                       capacity            REAL       NOT NULL);''')
        print("user数据表创建成功")
        self.conn.commit()

    def create_pile_table(self):
        # 检查表是否存在
        cursor = self.c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='pile_state'")
        for row in cursor:
            if row[0] == 1:
                print("pile_state数据表已存在")
                return
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
        self.c.execute(sql)
        print("pile_report表格创建成功")
        self.conn.commit()


my_connect = Connection()
