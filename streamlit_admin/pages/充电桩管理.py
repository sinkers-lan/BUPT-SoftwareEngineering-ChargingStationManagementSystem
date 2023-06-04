import streamlit as st
from typing import List
import asyncio
import requests
import json
import datetime
import threading
from utils import utils

HOST='http://10.28.136.251:8002'
st.set_page_config(
    page_title="显示充电桩状态",
    page_icon="👋",
)

# 设置全局变量
if 'stage' not in st.session_state:
    st.session_state['stage'] = 'login'
if 'token' not in st.session_state:
    st.session_state['token'] = '0'
if 'amount' not in st.session_state:
    st.session_state['amount'] = 0
if 'fast_pile_id' not in st.session_state:
    st.session_state['fast_pile_id'] = []
if 'slow_pile_id' not in st.session_state:
    st.session_state['slow_pile_id'] = []

def transform():
    pile_label = []
    amount = st.session_state.get('amount')
    fast_pile_id_list: List = st.session_state.get('fast_pile_id')
    slow_pile_id_list: List = st.session_state.get('slow_pile_id')
    pile_list = fast_pile_id_list + slow_pile_id_list
    for i in range(1, amount + 1):
        if i <= len(fast_pile_id_list):
            pile_label.append("快充充电桩" + chr(64 + i))
        else:
            pile_label.append("慢充充电桩" + chr(64 + i))
    return pile_list, pile_label


def send_post_request(pile_id, data_list):
    my_json = {'pile_id': pile_id}
    # print(f"==before {pile_id}=="+str(datetime.datetime.now().strftime("%H:%M:%S.%f")))
    data = utils.post(my_json, "/admin/queryPileState", st.session_state['token'])
    # print(f"==after {pile_id}=="+str(datetime.datetime.now().strftime("%H:%M:%S.%f")))
    if data['code'] == 1:
        target = data['data']
        target['pile_id'] = pile_id
        data_list.append(target)
    else:
        data_list = None
        return data_list

def query_pile_state(pile_id):
    my_json = {'pile_id': pile_id}
    data = utils.post(my_json, "/admin/queryPileState", st.session_state['token'])
    if data['code'] == 1:
        target = data['data']
        target['pile_id'] = pile_id
        return target
    else:
        st.error(data['message'])

def get_data():
    pile_list, pile_label = transform()
    tab_list = st.tabs(pile_label)
    fast_pile_list = []
    slow_pile_list = []
    for fast_pile_id in st.session_state['fast_pile_id']:
        fast_pile_list.append(query_pile_state(fast_pile_id))
    for slow_pile_id in st.session_state['slow_pile_id']:
        slow_pile_list.append(query_pile_state(slow_pile_id))
    fast_list = sorted(fast_pile_list, key=lambda x: x['pile_id'])
    slow_list = sorted(slow_pile_list, key=lambda x: x['pile_id'])
    data_list = fast_list + slow_list
    return data_list, tab_list


def display(workingState, totalChargeNum, totalChargeTime, totalCapacity, charge_mode):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("工作状态", workingState)
    col2.metric("累计充电次数", totalChargeNum)
    col3.metric("累计充电时间", totalChargeTime)
    col4.metric("充电总电量", totalCapacity)
    if charge_mode == 'F':
        col5.metric("充电模式", '快充')
    else:
        col5.metric("充电模式", '慢充')


if st.session_state['stage'] == 'login':
    st.title('管理员登录')
    st.markdown("#### 请输入管理员密码")
    password = st.text_input("密码")


    def login():
        if password:
            my_json = {"password": password}
            data = utils.post(my_json, "/admin/login")
            if data['code'] == 1:
                st.session_state['token'] = data['data']['token']
                st.session_state['stage'] = 'show_report'
                token = st.session_state.get('token')
                headers = {
                    "Authorization": token
                }
                data = utils.post({}, "/admin/queryPileAmount", token)
                if data['code'] == 1:
                    st.session_state['amount'] = data['data']['amount']
                    st.session_state['fast_pile_id'] = data['data']['fast_pile_id']
                    st.session_state['slow_pile_id'] = data['data']['slow_pile_id']
                else:
                    st.error(data['message'])
            else:
                st.error(data['message'])
        else:
            st.error("密码不能为空")
            return


    st.button("登录", on_click=login)
else:
    st.title("充电桩状态")
    tabs = []
    data_list, tab_list = get_data()


    def powerOn(args):
        my_json = {"pile_id": args}
        headers = {
            "Authorization": st.session_state['token']
        }
        data = utils.post(my_json, "/admin/powerOn", st.session_state['token'])
        if data['code'] == 0:
            st.error(data['message'])
        else:
            st.success("成功开启充电桩")


    def powerOff(args):
        my_json = {"pile_id": args}
        headers = {
            "Authorization": st.session_state['token']
        }
        data = utils.post(my_json, "/admin/powerOff", st.session_state['token'])
        if data['code'] == 0:
            st.error(data['message'])
        else:
            st.success("成功关闭充电桩")


    for tab, tab_content in zip(tab_list, data_list):
        with tab:
            if tab_content:
                display(tab_content['workingState'], tab_content['totalChargeNum'],
                        tab_content['totalChargeTime'], tab_content['totalCapacity'], tab_content['charge_mode'])
                if tab_content['workingState'] == '关闭':
                    st.button("开启", key=f"poweron_{tab_content['pile_id']}", on_click=powerOn,
                              args=(tab_content['pile_id'],))
                elif tab_content['workingState'] == '空闲':
                    st.button("关闭", key=f"poweroff_{tab_content['pile_id']}", on_click=powerOff,
                              args=(tab_content['pile_id'],))
            else:
                st.error("错误")
    st.divider()
    st.subheader("充电桩价格设置")


    def changePrice(low_price, mid_price, high_price):
        my_json = {"low_price": low_price, "mid_price": mid_price, "high_price": high_price}
        headers = {
            "Authorization": st.session_state['token']
        }
        data = utils.post(my_json, "/admin/setPrice", st.session_state['token'])
        if data['code'] == 1:
            st.success("成功设置充电桩价格")
        else:
            st.error(data['message'])


    low_price = st.number_input("谷时单价", step=0.1, value=1.0)
    mid_price = st.number_input("平时单价", step=0.1, value=0.7)
    high_price = st.number_input("峰时单价", step=0.1, value=0.4)
    # print(datetime.datetime.now().strftime("%H:%M:%S.%f"))
    # print("----end----")
    if low_price == 1.0 and mid_price == 0.7 and high_price == 0.4:
        st.divider()
    else:
        changePrice(low_price, mid_price, high_price)
