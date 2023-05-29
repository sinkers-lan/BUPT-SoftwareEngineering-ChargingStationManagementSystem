import requests
import json

# HOST = "http://10.112.241.69:8002"
# HOST = "http://123.56.44.128:8002"
HOST = "http://127.0.0.1:8002"

def post(my_json: dict, path: str):
    return requests.post(url=HOST + path, data=json.dumps(my_json)).json()
