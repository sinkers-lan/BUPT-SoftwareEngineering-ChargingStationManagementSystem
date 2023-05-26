import streamlit as st
import requests
import json

HOST = "http://127.0.0.1:8002"
if st.session_state['stage'] == "用户登录":
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户登录")
    phone = st.text_input("手机号")
    password = st.text_input("密码")


    def login(args):
        if args == "logon":
            st.session_state['stage'] = "用户注册"
            return
        if not phone:
            st.error("手机号不能为空")
            return
        if len(phone) != 11 or not phone.isdigit():
            st.error("手机号格式不正确")
            return
        if not password:
            st.error("密码不能为空")
            return
        if phone and password:
            my_json = {"user_name": phone, "password": password}
            data = requests.post(url=HOST + "/user/login", data=json.dumps(my_json)).json()
            if data['code'] == 1:
                st.session_state['user'] = phone
                st.session_state['token'] = data['data']['token']
                st.session_state['stage'] = "提交充电请求"
            else:
                st.error(data['message'])
            pass


    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        st.button("登录", on_click=login, args=("login",))
    with col2:
        st.button("注册", on_click=login, args=("logon",))
else:
    st.markdown("# Page 2 ❄️")
    st.sidebar.markdown("# Page 2 ❄️")