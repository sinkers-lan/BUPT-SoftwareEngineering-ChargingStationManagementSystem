import streamlit as st
from utils import utils


def change_capacity():
    data = {
        "car_id": st.session_state['car'],
        "capacity": st.session_state['capacity_submit']
    }
    data_ = utils.post(data, path="/user/changeCapacity", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
    else:
        st.success("修改成功")
        st.session_state['capacity'] = st.session_state['capacity_submit']


st.markdown('### 更改车辆信息')
st.markdown('---')

if st.session_state['stage'] == "用户登录" or st.session_state['stage'] == "用户注册":
    st.write("请先登录")
    st.stop()

with st.form("change_capacity"):
    st.markdown("#### 容量")
    st.slider('电车总容量 (度)', 0.0, 150.0, st.session_state['capacity'], 0.1,
              key='capacity_submit')
    st.form_submit_button("更改容量", on_click=change_capacity)
