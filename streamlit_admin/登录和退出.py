import streamlit as st
import requests
import json
from utils import utils

st.set_page_config(
    page_title="管理员客户端",
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

if st.session_state['stage'] == 'login':
    st.title('管理员登录')
    st.markdown("#### 请输入管理员密码")
    password = st.text_input("密码", type="password")


    def login():
        if password:
            my_json = {"password": password}
            data = utils.post(my_json, "/admin/login")
            if data['code'] == 1:
                st.session_state['token'] = data['data']['token']
                st.session_state['stage'] = 'show_report'
                token = st.session_state.get('token')
                data = utils.post({}, "/admin/queryPileAmount", token)
                if data['code'] == 1:
                    st.session_state['amount'] = data['data']['amount']
                    st.session_state['fast_pile_id'] = [i['pile_id'] for i in data['data']['fast_pile_id']]
                    st.session_state['slow_pile_id'] = [i['pile_id'] for i in data['data']['slow_pile_id']]
                else:
                    st.error(data['message'])
            else:
                st.error(data['message'])
        else:
            st.error("密码不能为空")
            return


    st.button("登录", on_click=login)
else:
    def exit():
        headers = {
            "Authorization": st.session_state['token']
        }
        data = utils.post({}, "/admin/logout", st.session_state['token'])
        if data['code'] == 1:
            st.success(data['message'])
            st.session_state['stage'] = "login"
        else:
            st.error(data['message'])


    st.title("管理员退出")
    img = 'https://img.mjj.today/2023/05/27/47d01dd60f3f5e83da821f40d829fe7c.png'
    st.image(img, caption='您现在处于登录状态')
    st.button("退出", on_click=exit)
