import requests
import json

# HOST = "http://10.112.241.69:8002"
# HOST = "http://123.56.44.128:8002"
HOST = "http://127.0.0.1:8002"


def post(my_json: dict, path: str, token=None):
    print(token)
    if token is not None:
        headers = {
            # "Content-Type": "application/json",
            "Authorization": token
        }
        return requests.post(url=HOST + path, data=json.dumps(my_json), headers=headers).json()
    else:
        return requests.post(url=HOST + path, data=json.dumps(my_json)).json()
