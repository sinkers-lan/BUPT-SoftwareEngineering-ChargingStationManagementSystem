import streamlit as st
from typing import List
import json
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import utils
from utils.utils import post
import threading

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体
plt.rcParams["axes.unicode_minus"] = False  # 该语句解决图像中的“-”负号的乱码问题
# TODO:也许datetime.today()需要替换成虚拟时间
st.set_page_config(
    page_title="查看报表",
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


def check_all_zeros(df):
    return (df == 0).all().all()


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


def query_pile_report(pile_id, start_date, end_date):
    my_json = {'pile_id': pile_id, 'start_date': start_date, 'end_date': end_date}
    data = utils.post(my_json, "/admin/queryReport", st.session_state['token'])
    if data['code'] == 1:
        target = data['data']
        target['pile_id'] = pile_id
        return target
    else:
        st.error(data['message'])


# 展示费用
def display_fee(data_list, labels):
    # print("======")
    print(data_list)
    df = pd.DataFrame(data_list)
    print(df)
    sum_charge = df['total_charge_fee'].sum()
    sum_service = df['total_service_fee'].sum()
    sum_fee = df['total_fee'].sum()
    # labels=['快充电桩A','快充电桩B','慢充电桩C','慢充电桩D','慢充电桩E']
    colors = ['#f7dc6f', '#48c9b0', '#f1948a', '#5faee3', '#707b7c']
    st.subheader("全部充电桩费用信息")
    col1, col2, col3 = st.columns(3)
    col1.metric("累计充电费用", sum_charge)
    col2.metric("累计服务费用", sum_service)
    col3.metric("累计总费用", sum_fee)
    st.divider()

    fig = plt.figure()
    data = df['total_charge_fee']
    result = check_all_zeros(data)
    # 存在一个全0，则不按饼状图显示
    if not result:
        st.subheader("累计充电费用")
        plt.pie(data, labels=labels, colors=colors,
                autopct=lambda x: '{:.0f}'.format(x * data.sum() / 100),
                shadow=True, startangle=90)  # startangle=90则从y轴正方向画起
        plt.axis('equal')  # 该行代码使饼图长宽相等
        plt.legend(loc="upper left", fontsize=10, bbox_to_anchor=(1.1, 1.05), borderaxespad=0.3)  # 添加图例
        st.pyplot(fig)
        st.divider()
        st.subheader("累计服务费用")
        fig = plt.figure()
        data = df['total_service_fee']
        plt.pie(data, labels=labels, colors=colors,
                autopct=lambda x: '{:.0f}'.format(x * data.sum() / 100),
                shadow=True, startangle=90)  # startangle=90则从y轴正方向画起
        plt.axis('equal')  # 该行代码使饼图长宽相等
        plt.legend(loc="upper left", fontsize=10, bbox_to_anchor=(1.1, 1.05), borderaxespad=0.3)  # 添加图例
        st.pyplot(fig)
        st.divider()
        st.subheader("累计总费用")
        fig = plt.figure()
        data = df['total_fee']
        plt.pie(data, labels=labels, colors=colors,
                autopct=lambda x: '{:.0f}'.format(x * data.sum() / 100),
                shadow=True, startangle=90)  # startangle=90则从y轴正方向画起
        plt.axis('equal')  # 该行代码使饼图长宽相等
        plt.legend(loc="upper left", fontsize=10, bbox_to_anchor=(1.1, 1.05), borderaxespad=0.3)  # 添加图例
        st.pyplot(fig)
    else:
        st.info("当前日期没有报表数据")
        df = df[['total_charge_fee', 'total_service_fee', 'total_fee']]
        df.columns = ['累计充电费用', '累计服务费用', '累计总费用']
        df = df.transpose()
        df.columns = labels
        st.write(df.transpose())


# 展示充电次数
def display_charge(data_list, labels):
    df = pd.DataFrame(data_list)
    df = df[['total_charge_num', 'total_charge_time', 'total_capacity']]
    df.columns = ['累计充电次数', '累计充电时长', '累计充电量']
    df = df.transpose()
    df.columns = labels
    st.write(df.transpose())
    result = check_all_zeros(df)
    if not result:
        st.bar_chart(df, width=1)
    else:
        st.info("当前日期没有报表数据")


def send_post_request(pile_id, start_date, end_date, data_list, header):
    my_json = {'pile_id': pile_id, 'start_date': start_date, 'end_date': end_date}
    # print("==before=="+str(pile_id)+str(datetime.datetime.now().strftime("%H:%M:%S.%f")))
    data = utils.post(my_json, "/admin/queryReport", st.session_state['token'])
    # print("==after=="+str(pile_id)+str(datetime.datetime.now().strftime("%H:%M:%S.%f")))
    if data['code'] == 1:
        # print("success")
        target = data['data']
        target['pile_id'] = pile_id
        data_list.append(target)
    else:
        print("error")
        data_list = None
        return data_list

def get_data(start_date, end_date):
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    fast_pile_list = []
    slow_pile_list = []
    for fast_pile_id in st.session_state['fast_pile_id']:
        fast_pile_list.append(query_pile_report(fast_pile_id, start_date, end_date))
    for slow_pile_id in st.session_state['slow_pile_id']:
        slow_pile_list.append(query_pile_report(slow_pile_id, start_date, end_date))
    fast_list = sorted(fast_pile_list, key=lambda x: x['pile_id'])
    slow_list = sorted(slow_pile_list, key=lambda x: x['pile_id'])
    data_list = fast_list + slow_list
    return data_list


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
    st.title("查看报表")
    col1, col2 = st.columns(2)
    with col1:
        option = st.selectbox(
            "显示方式",
            ("日", "月", "年")
        )
    with col2:
        start_date = st.date_input("起始日期", datetime.date.today())
    if option == '日':
        Days = datetime.timedelta(days=0)
    # 一月按30天计算
    elif option == '月':
        Days = datetime.timedelta(days=30)
    else:
        Days = datetime.timedelta(days=365)
    end_date = start_date + Days
    tabs = ['费用', '充电']
    tab1, tab2, = st.tabs(tabs)
    data_list = get_data(start_date, end_date)
    pile_list, labels = transform()
    with tab1:
        st.subheader("报表时间" + str(start_date) + "~" + str(end_date))
        display_fee(data_list, labels)
    with tab2:
        st.subheader("报表时间" + str(start_date) + "~" + str(end_date))
        display_charge(data_list, labels)
