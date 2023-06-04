import datetime
from enum import Enum
import streamlit as st
import requests
import json

HOST = "http://10.28.136.251:8002"


def post(my_json: dict, path: str, token=None) -> dict:
    # print(token)
    if token is not None:
        headers = {
            # "Content-Type": "application/json",
            "Authorization": token
        }
        response = requests.post(url=HOST + path, data=json.dumps(my_json), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(response.text)
        # return requests.post(url=HOST + path, data=json.dumps(my_json), headers=headers).json()
    else:
        # return requests.post(url=HOST + path, data=json.dumps(my_json)).json()
        response = requests.post(url=HOST + path, data=json.dumps(my_json))
        if response.status_code == 200:
            return response.json()
        else:
            st.error(response.text)