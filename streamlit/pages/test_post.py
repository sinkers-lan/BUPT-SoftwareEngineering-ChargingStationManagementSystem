from utils import utils
import streamlit as st


def query_car_state():
    data = {
        "car_id": st.session_state['car']
    }
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


def end_charging():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/endCharging", token=st.session_state['token'])
    st.write(data_)


def change_charging_mode():
    data = {
        "car_id": st.session_state['car'],
        "request_mode": "T"
    }
    data_ = utils.post(data, path="/user/changeChargingMode", token=st.session_state['token'])
    st.write(data_)


def change_charging_amount():
    data = {
        "car_id": st.session_state['car'],
        "request_amount": 10.0
    }
    data_ = utils.post(data, path="/user/changeChargingAmount", token=st.session_state['token'])
    st.write(data_)


def get_charging_state():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/getChargingState", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
    st.session_state['bill_id'] = data_['data']['bill_id']
    st.write(data_)


def get_pay_bill():
    if "bill_id" not in st.session_state:
        st.write("请先获取账单")
        return
    data = {
        "bill_id": st.session_state['bill_id']
    }
    data_ = utils.post(data, path="/user/getPayBill", token=st.session_state['token'])
    st.write(data_)


def get_total_bill():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/getTotalBill", token=st.session_state['token'])
    st.write(data_)


def get_detail_bill():
    data = {
        "bill_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/getDetailBill", token=st.session_state['token'])
    st.write(data_)


if "car" not in st.session_state:
    st.write("请先登录")
else:
    st.button("queryCarState", on_click=query_car_state)
    st.button("chargingRequest", on_click=charging_request)
    st.button("beginCharging", on_click=begin_charging)
    st.button("endCharging", on_click=end_charging)
    st.button("changeChargingMode", on_click=change_charging_mode)
    st.button("changeChargingAmount", on_click=change_charging_amount)
    st.button("getChargingState", on_click=get_charging_state)
    st.button("getPayBill", on_click=get_pay_bill)
    st.button("getTotalBill", on_click=get_total_bill)
