from utils import utils
import streamlit as st


def query_car_state():
    data = {
        "car_id": "京JG2431"
    }
    # print(data)
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    st.write(data_)


def charging_request():
    data = {
        "car_id": "京JG2431",
        "request_amount": 10.0,
        "request_mode": "快充"
    }
    data_ = utils.post(data, path="/user/chargingRequest", token=st.session_state['token'])
    st.write(data_)


def begin_charging():
    data = {
        "car_id": "京JG2431"
    }
    data_ = utils.post(data, path="/user/beginCharging", token=st.session_state['token'])
    st.write(data_)


st.button("queryCarState", on_click=query_car_state)
st.button("chargingRequest", on_click=charging_request)
st.button("beginCharging", on_click=begin_charging)
