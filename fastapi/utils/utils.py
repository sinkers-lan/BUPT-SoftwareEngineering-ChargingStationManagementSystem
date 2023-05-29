# 用于生成token
import jwt
import datetime
import hashlib


def generate_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload=payload, key="hello_my_teammates", algorithm='HS256')
    return token


def decode_token(token):
    return jwt.decode(token, key="hello_my_teammates", algorithms='HS256')


def hash_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    str_md5 = md5.hexdigest()
    return str_md5


def generate_bill_ls(bill_id):
    code_qz = 'DD'
    code_sj = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return code_qz + code_sj + str(bill_id)


def formate_datetime(time_stamp: float):
    return datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
