import streamlit as st
from typing import List
import json
import pandas as pd
import numpy as np
from utils import utils

st.set_page_config(
    page_title="查看队列",
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


def get_data():
    data = utils.post({}, "/admin/queryQueueState", st.session_state['token'])
    if data['code'] == 1:
        state_list = data['data']['state_list']
    else:
        st.error(data['message'])
        state_list = None
    return state_list


def process_df(df):
    df = df.drop('pile_id', axis=1)
    df = df.drop('car_state', axis=1)
    df.columns = ['用户ID', '车辆总电量', '充电量', '充电模式', '等待时长']
    return df


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
    st.title("查看队列")
    pile_list, tabs = transform()
    tab_list = st.tabs(tabs)
    state_list = get_data()
    print(state_list)
    if state_list:
        df = pd.DataFrame(state_list)
        i = 0
        for tab in tab_list:
            with tab:
                data = df[df['pile_id'] == pile_list[i]].reset_index(drop=True)
                data = process_df(data)
                st.table(data)
                st.divider()
                st.subheader("等待区队列")
                data = df[df['car_state'] == '等待区'].reset_index(drop=True)
                data = process_df(data)
                st.table(data)
                i += 1
    else:
        st.info("当前充电桩没有车辆")
