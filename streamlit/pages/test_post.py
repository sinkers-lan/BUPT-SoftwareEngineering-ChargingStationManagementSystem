from utils import utils
import streamlit as st

def query_car_state():
    data = {
        "car_id": "京JG2431"
    }
    print(data)
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    print(data_)

st.button("queryCarState", on_click=query_car_state)