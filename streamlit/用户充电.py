import random
import json
import re
import streamlit as st
import datetime
import time
import asyncio
import requests
import threading
# from streamlit_autorefresh import st_autorefresh
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx, RerunException

# HOST = "http://10.112.241.69:8002"
# HOST = "http://123.56.44.128:8002"
HOST = "http://127.0.0.1:8002"
# 设置全局变量
if 'stage' not in st.session_state:
    st.session_state['stage'] = '用户登录'
if 'mode' not in st.session_state:
    st.session_state['mode'] = '快充'
if 'degree' not in st.session_state:
    st.session_state['degree'] = 0.0
if 'capacity' not in st.session_state:
    st.session_state['capacity'] = 45.0
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'car' not in st.session_state:
    st.session_state['car'] = None
if 'wait' not in st.session_state:
    st.session_state['wait'] = 20
if 'wait_i' not in st.session_state:
    st.session_state['wait_i'] = 20
if "token" not in st.session_state:
    st.session_state['token'] = None

# 设置不同充电阶段的进度侧边栏
st.sidebar.markdown("## 使用流程")
if st.session_state['stage'] == '用户登录' or st.session_state['stage'] == "用户注册":
    st.sidebar.warning("用户登录")
    st.sidebar.info("提交充电请求")
    st.sidebar.info("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == '提交充电请求':
    st.sidebar.success("用户登录")
    st.sidebar.warning("提交充电请求")
    st.sidebar.info("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == '等待叫号':
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.warning("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == '开始充电':
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.success("等待叫号")
    st.sidebar.warning("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == '结束充电并缴费':
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.success("等待叫号")
    st.sidebar.success("开始充电")
    st.sidebar.warning("结束充电并缴费")

# 未登录阶段
if st.session_state['stage'] == '用户登录':
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

if st.session_state['stage'] == '用户注册':
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户注册")
    phone = st.text_input("手机号")
    password = st.text_input("密码")
    car = st.text_input("车牌号")
    capacity = st.slider('电车电池总容量 (度)', 15.0, 60.0, 45.0, 0.1, key="capacity_form")


    def login(args):
        print(args)
        if args == "login":
            st.session_state['stage'] = "用户登录"
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
        if not car:
            st.error("车牌号不能为空")
            return
        # pattern = "^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼A-Z]{1}[A-Z]{1}\s{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$"
        pattern = "([京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼]" \
              "{1}(([A-HJ-Z]{1}[A-HJ-NP-Z0-9]{5})|([A-HJ-Z]{1}(([DF]{1}[A-HJ-NP-Z0-9]{1}[0-9]{4})|([0-9]{5}[DF]" \
              "{1})))|([A-HJ-Z]{1}[A-D0-9]{1}[0-9]{3}警)))|([0-9]{6}使)|((([沪粤川云桂鄂陕蒙藏黑辽渝]{1}A)|鲁B|闽D|蒙E|蒙H)" \
              "[0-9]{4}领)|(WJ[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼·•]{1}[0-9]{4}[TDSHBXJ0-9]{1})" \
              "|([VKHBSLJNGCE]{1}[A-DJ-PR-TVY]{1}[0-9]{5})"
        if not re.findall(pattern, car):
            st.error("车牌号格式不正确")
            return
        if capacity == 0:
            st.error("电车电池容量不能为零")
            return
        my_json = {"user_name": phone, "password": password, "car_id": car, "capacity": capacity}
        data = requests.post(url=HOST + "/user/register", data=json.dumps(my_json)).json()
        if data['code'] == 1:
            st.session_state['user'] = phone
            st.session_state['token'] = data['data']['token']
            st.session_state['capacity'] = capacity
            st.session_state['car'] = car
            st.session_state['stage'] = "提交充电请求"
        else:
            st.error(data['message'])
        pass


    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        st.button("登录", on_click=login, args=("login",))
    with col2:
        st.button("注册", on_click=login, args=("logon",))


# 未提交充电请求阶段
if st.session_state['stage'] == '提交充电请求':
    st.markdown("#### 提交充电请求")
    st.write("")
    st.session_state['mode'] = st.radio("充电模式 👇", ('快充', '慢充'), help="快充 (30 度/小时), 慢充 (7 度/小时)")
    # , horizontal=True
    st.write("")
    st.session_state['degree'] = st.slider('请求充电量 (度)', 0.0, st.session_state['capacity'], 0.0, 0.1)
    st.info(f"请确认您要提交的充电请求：{st.session_state['mode']} {st.session_state['degree']} (度)")


    def confirm_on_click():
        if st.session_state['degree'] == 0:
            st.error("不能提交0度的充电请求")
        else:
            # st.success('正在提交充电请求...')
            st.session_state['stage'] = '等待叫号'


    confirm = st.button("提交充电请求", on_click=confirm_on_click)


# 等待叫号阶段
if st.session_state['stage'] == '等待叫号':
    st.markdown("#### 等待叫号")

    st.write("")
    hao = 'f7'


    def show_hao(hao_in, mode_in, degree_in):
        st.write("您的排队号码是:", hao_in, "，您的充电模式:", mode_in, "，您的请求充电量：", degree_in, " (度)")


    show_hao(hao, st.session_state['mode'], st.session_state['degree'])


    def change_mode_on_click():
        st.session_state['stage'] = "修改充电模式"


    def change_degree_on_click():
        def degree_form_callback():
            if st.session_state['degree'] == st.session_state['degree_form']:
                st.warning("没有修改充电电量")
            else:
                st.success(f"修改充电电量为:{st.session_state['degree_form']}")
                st.session_state['degree'] = st.session_state['degree_form']

        with st.form(key='my_form2'):
            st.info("修改充电模式不用重新排队。是否要修改充电电量？")
            # capacity = st.slider('电车电池总容量 (度)', 15.0, 60.0, 45.0, 0.1, key="capacity_form")
            st.slider('请求充电量 (度)', 0.0, st.session_state['capacity'], st.session_state['degree'], 0.1,
                      key="degree_form")
            st.form_submit_button(label='确认修改', on_click=degree_form_callback)


    col1, col2, col3 = st.columns(3)
    with col1:
        change_mode = st.button("修改充电模式", on_click=change_mode_on_click)
    with col2:
        change_degree = st.button("修改充电量", on_click=change_degree_on_click)
    with col3:
        cancel = st.button("取消本次充电")
        if cancel:
            def cancel_confirm_on_click():
                st.session_state['stage'] = "提交充电请求"
                # 取消叫号请求发送


            st.warning("是否确认取消充电请求？取消充电请求本次排队号作废")
            st.button("确定取消", on_click=cancel_confirm_on_click)
            st.button("不取消")

    st.write("")
    st.markdown("##### 等待进度")
    st.session_state['wait_i'] = st.session_state['wait']


    def get_wait_num():
        wait = requests.get(HOST + "/wait").json()['num']
        # wait = 10
        return wait


    def wait_num_on_click():
        if st.session_state['wait'] != 0:
            st.session_state['wait'] = get_wait_num()


    def begin_on_click():
        if st.session_state['wait'] == 0:
            st.balloons()
            st.success("成功开始充电")
            st.session_state['stage'] = "开始充电"
        else:
            st.warning("您的状态未满足充电要求")


    st.session_state['wait'] = get_wait_num()

    st.button("查看等候数量", on_click=wait_num_on_click)
    st.write("前车等待数量:" + str(st.session_state['wait']))
    st.button("开始充电", on_click=begin_on_click)

    thread_state = 0


    def heart_beat():
        # 打印当前时间
        st.session_state['wait'] = get_wait_num()
        print(st.session_state['wait'], time.strftime('%Y-%m-%d %H:%M:%S'))
        if st.session_state['wait'] != 0:
            timer = threading.Timer(1, heart_beat)
            add_script_run_ctx(timer, get_script_run_ctx())
            global thread_state
            thread_state = 1
            timer.start()


    if thread_state == 0:
        heart_beat()

if st.session_state['stage'] == "修改充电模式":
    def mode_form_callback():
        if st.session_state['mode'] == st.session_state['mode_form']:
            st.warning("没有修改充电模式")
        else:
            st.success(f"修改充电模式为:{st.session_state['mode_form']}")
            st.session_state['mode'] = st.session_state['mode_form']


    with st.form(key='change_mode_form'):
        st.warning("是否要修改充电模式？修改充电模式将重新排队")
        if st.session_state['mode'] == '快充':
            idx = 0
        else:
            idx = 1
        st.radio("修改充电模式 👇", ('快充', '慢充'), help="快充 (30 度/小时), 慢充 (7 度/小时)", index=idx,
                 key="mode_form")
        st.form_submit_button(label='确认修改', on_click=mode_form_callback)


    def return_on_click():
        st.session_state['stage'] = "等待叫号"
    st.button("返回")



if st.session_state['stage'] == "开始充电":
    st.markdown("#### 正在充电中")
    # st.button("刷新页面")
    cancel = st.button("停止充电")
    if cancel:
        def cancel_confirm_on_click():
            st.session_state['stage'] = "提交充电请求"
            # 取消叫号请求发送


        st.warning("是否确认停止充电？停止充电将直接进入缴费流程，如要再次充电需重新排队")
        st.button("确定停止", on_click=cancel_confirm_on_click)
        st.button("不停止")

    st.markdown("#### 充电进度")
    degree = st.session_state['degree']
    i = 0.0
    my_bar = st.progress(0)
    # , text="正在等待 " + str(i) + "/" + str(degree)
    while i < degree:
        time.sleep(0.2)
        i += 0.1
        if i >= degree:
            st.balloons()
            st.session_state['stage'] = "结束充电并缴费"
        if i > degree:
            i = degree
        my_bar.progress(i / degree)

if st.session_state['stage'] == "结束充电并缴费":
    st.markdown("#### 结束充电并缴费")
