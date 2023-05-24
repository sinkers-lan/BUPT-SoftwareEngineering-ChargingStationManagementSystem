# 用于生成token
import jwt
import datetime


def generate_token(user):
    payload = {
        'user_name': user.user_name,
        'exp': datetime.datetime.now() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload=payload, key="hello_my_teammates", algorithm='HS256')
    return token


def decode_token(token):
    return jwt.decode(token, key="hello_my_teammates", algorithms='HS256')
