from utils import utils
import streamlit as st


def query_car_state():
    data = {
        "car_id": st.session_state['car']
    }
    # print(data)
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    st.write(data_)


def charging_request():
    data = {
        "car_id": st.session_state['car'],
        "request_amount": 20.0,
        "request_mode": "F"
    }
    data_ = utils.post(data, path="/user/chargingRequest", token=st.session_state['token'])
    st.write(data_)


def begin_charging():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/beginCharging", token=st.session_state['token'])
    st.write(data_)


def pay_the_bill():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/getPayBill", token=st.session_state['token'])
    st.write(data_)


st.button("queryCarState", on_click=query_car_state)
st.button("chargingRequest", on_click=charging_request)
st.button("beginCharging", on_click=begin_charging)
st.button("getPayBill", on_click=pay_the_bill)
