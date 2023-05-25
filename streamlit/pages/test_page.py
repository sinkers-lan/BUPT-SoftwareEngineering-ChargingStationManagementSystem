import streamlit as st
import requests
import json

HOST = "http://10.112.241.69:8003"
my_json = {"user_name": "123", "password": "abc"}
if __name__ == "__main__":
    data = requests.post(url=HOST + "/user/login", data=json.dumps(my_json)).json()
    print(data)
