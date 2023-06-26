from app.dao.connection import my_connect


# conn = sqlite3.connect('SoftwareEngineering.db')
# print("数据库打开成功")
# c = conn.cursor()
# conn.close()


"""创建表"""
def create_table():
    # 检查表是否存在
    cursor = my_connect.c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='user'")
    for row in cursor:
        if row[0] == 1:
            print("数据表user已存在")
            return
    my_connect.c.execute('''CREATE TABLE user
               (user_id             Integer PRIMARY KEY autoincrement,
               user_name           TEXT     NOT NULL,
               hash_password       TEXT     NOT NULL,
               car_id             TEXT     NOT NULL,
               capacity            REAL       NOT NULL);''')
    print("数据表创建成功")
    my_connect.conn.commit()

#
# c.execute('''CREATE TABLE user
#        (user_id             Integer PRIMARY KEY autoincrement,
#        user_name           TEXT     NOT NULL,
#        hash_password       TEXT     NOT NULL,
#        car_id             TEXT     NOT NULL,
#        capacity            REAL       NOT NULL);''')
# print("数据表创建成功")
# conn.commit()
# conn.close()

# c.execute('''DROP TABLE user;''')
# print("数据表修改成功")
# conn.commit()
# conn.close()

def login(user_name: str, hash_password: str):
    # 查看用户名对应的hashed密码
    cursor = my_connect.c.execute(f"select * from user where user_name = '{user_name}'")
    # conn.close()
    for row in cursor:
        if hash_password == row[2]:
            return {
                "code": 1,
                "message": "登录成功",
                "data": {
                    "user_id": row[0],
                    "user_name": row[1],
                    "token": None,
                    "car_id": row[3],
                    "car_capacity": row[4]
                }
            }
        else:
            return {
                "code": 0,
                "message": "密码不正确"
            }
    return {
        "code": 0,
        "message": "用户未注册"
    }


def logon(user_name: str, hash_password: str, car_id: str, capacity: float) -> dict:
    # 查看用户名和车辆ID是否有重复

    cursor = my_connect.c.execute(f"select * from user where user_name = '{user_name}'")
    for row in cursor:
        print(row)
        print("用户名重复")
        return {
            "code": 0,
            "message": "用户名重复"
        }
    cursor = my_connect.c.execute(f"select * from user where car_id = '{car_id}'")
    for row in cursor:
        print("车牌号重复")
        return {
            "code": 0,
            "message": "车牌号重复"
        }
    my_connect.c.execute(f"INSERT INTO user (user_name,hash_password,car_id,capacity) \
           VALUES ('{user_name}', '{hash_password}', '{car_id}', {capacity} )")
    print("数据表插入成功")
    my_connect.conn.commit()
    user_id = 0
    cursor = my_connect.c.execute(f"select user_id from user where user_name = '{user_name}'")
    for row in cursor:
        user_id = row[0]
    return {
        "code": 1,
        "message": "注册成功",
        "data": {
            "user_id": user_id,
            "user_name": user_name,
            "token": None,
            "car_id": car_id,
            "car_capacity": capacity
        }
    }


def get_car_info(car_id: str):
    """返回user_id, capacity"""
    cursor = my_connect.c.execute(f"select user_id, capacity from user where car_id = '{car_id}'")
    for row in cursor:
        return row[0], row[1]
    raise Exception("No such car_id")


def change_capacity(car_id: int, capacity: float):
    my_connect.c.execute(f"update user set capacity = {capacity} where car_id = '{car_id}'")
    my_connect.conn.commit()
    return {"code": 1, "message": "修改成功", "data": {"car_capacity": capacity}}
