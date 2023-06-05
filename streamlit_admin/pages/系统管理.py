import streamlit as st
from utils import utils
from typing import List

st.set_page_config(
    page_title="充电桩系统操作",
    page_icon="👋",
)

if 'stage' not in st.session_state:
    st.session_state['stage'] = 'login'

if st.session_state['stage'] == 'login':
    st.warning("请先登录")
    st.stop()

st.title("充电桩系统操作")
st.markdown("---")


def accelerate():
    data = {
        "rate": st.session_state['rate']
    }
    data_ = utils.post(data, path="/system/accelerate")
    st.write(data_)


rate = st.slider("系统时间倍率", 1, 500, 1, 1, key="rate", on_change=accelerate)



def get_time():
    data = utils.post({}, path="/system/getTime")
    st.write(data)


st.button("获取系统时间", on_click=get_time, use_container_width=True)


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


def pile_crash(pile_id):
    data = {
        "pile_id": pile_id
    }
    data_ = utils.post(data, path="/admin/powerCrash")
    st.write(data_)


def pile_repair(pile_id):
    data = {
        "pile_id": pile_id
    }
    data_ = utils.post(data, path="/admin/powerOn")
    st.write(data_)


pile_id_list, pile_label = transform()
print(pile_id_list)
pile_num = len(pile_id_list)
for i in range(pile_num):
    st.markdown(f"##### {pile_label[i]}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"损坏", key=f"pile_crash{i}", use_container_width=True):
            pile_crash(pile_id_list[i])
    with col2:
        if st.button(f"维修完毕", key=f"pile_repair{i}", use_container_width=True):
            pile_repair(pile_id_list[i])
