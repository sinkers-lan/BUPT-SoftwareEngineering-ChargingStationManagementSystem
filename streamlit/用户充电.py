import re

import streamlit as st
import time

from utils import utils

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
if "backward" not in st.session_state:
    st.session_state['backward'] = "提交充电请求"
if "error_flag" not in st.session_state:
    st.session_state['error_flag'] = False
if "error_info" not in st.session_state:
    st.session_state['error_info'] = ""
if "warning_flag" not in st.session_state:
    st.session_state['warning_flag'] = False
if "warning_info" not in st.session_state:
    st.session_state['warning_info'] = ""
if "info_flag" not in st.session_state:
    st.session_state['info_flag'] = False
if "info_info" not in st.session_state:
    st.session_state['info_info'] = ""
if "success_flag" not in st.session_state:
    st.session_state['success_flag'] = False
if "success_info" not in st.session_state:
    st.session_state['success_info'] = ""
if "loop" not in st.session_state:
    st.session_state['loop'] = False

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
if st.session_state['stage'] == '等待叫号' or st.session_state['stage'] == "修改充电模式" or st.session_state['stage'] == "修改充电量":
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.warning("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == '开始充电' or st.session_state['stage'] == "准备充电" or st.session_state[
    'stage'] == "取消充电_充电区":
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


def show_info():
    if st.session_state['error_flag']:
        st.error(st.session_state['error_info'])
    if st.session_state['warning_flag']:
        st.warning(st.session_state['warning_info'])
    if st.session_state['info_flag']:
        st.info(st.session_state['info_info'])
    if st.session_state['success_flag']:
        st.success(st.session_state['success_info'])
    st.session_state['error_flag'] = False
    st.session_state['warning_flag'] = False
    st.session_state['info_flag'] = False
    st.session_state['success_flag'] = False


def user_login():
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户登录")
    phone = st.text_input("手机号")
    password = st.text_input("密码", type="password")

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
            data = utils.post(my_json=my_json, path="/user/login")
            if data['code'] == 1:
                st.session_state['user'] = phone
                st.session_state['token'] = data['data']['token']
                st.session_state['car'] = data['data']['car_id']
                st.session_state['capacity'] = data['data']['car_capacity']
                st.session_state['stage'] = "提交充电请求"
            else:
                st.error(data['message'])
            pass

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        st.button("登录", on_click=login, args=("login",))
    with col2:
        st.button("注册", on_click=login, args=("logon",))


def user_logon():
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户注册")
    phone = st.text_input("手机号")
    password = st.text_input("密码", type="password")
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
        data = utils.post(my_json=my_json, path="/user/login")
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


def commit_charging_request():
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


def show_hao(hao_in, mode_in, degree_in):
    st.write("您的排队号码是:", hao_in, "，您的充电模式:", mode_in, "，您的请求充电量：", degree_in, " (度)")


def backward(default_stage: str):
    st.write("20秒后超时返回叫号界面")
    with st.empty():
        if st.session_state['loop']:
            for seconds in range(0, 20):
                st.write(f"⏳ {20 - seconds}")
                time.sleep(1)
                # if not st.session_state['loop']:
                #     break
            else:
                st.write("操作超时")
                st.session_state['stage'] = default_stage
                st.experimental_rerun()
        else:
            st.session_state['stage'] = st.session_state['backward']
            st.experimental_rerun()


def waiting():
    st.markdown("#### 等待叫号")
    show_info()
    # st.write("")
    st.session_state['wait'] = 'f7'
    show_hao(st.session_state['wait'], st.session_state['mode'], st.session_state['degree'])

    def change_mode_on_click():
        st.session_state['stage'] = "修改充电模式"
        st.session_state['loop'] = True

    def change_degree_on_click():
        st.session_state['stage'] = "修改充电量"
        st.session_state['loop'] = True

    def cancel_on_click():
        st.session_state['stage'] = "取消充电"
        st.session_state['loop'] = True

    col1, col2, col3 = st.columns(3)
    with col1:
        change_mode = st.button("修改充电模式", on_click=change_mode_on_click)
    with col2:
        change_degree = st.button("修改充电量", on_click=change_degree_on_click)
    with col3:
        cancel = st.button("取消本次充电", on_click=cancel_on_click)

    st.write("")
    st.markdown("##### 等待进度")
    st.session_state['wait_i'] = st.session_state['wait']

    def get_wait_num():
        # wait = requests.get(HOST + "/wait").json()['num']
        wait = 10
        return wait

    st.session_state['wait'] = get_wait_num()

    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.2)
        my_bar.progress(percent_complete + 1)
    else:
        st.balloons()
        st.session_state['stage'] = "准备充电"
        st.experimental_rerun()


def change_mode():
    st.markdown("#### 等待叫号")
    show_hao(st.session_state['wait'], st.session_state['mode'], st.session_state['degree'])

    def mode_form_callback():
        if st.session_state['mode'] == st.session_state['mode_form']:
            # st.warning("没有修改充电模式")
            st.session_state['warning_flag'] = True
            st.session_state['warning_info'] = "没有修改充电模式"
        else:
            # st.success(f"修改充电模式为:{st.session_state['mode_form']}")
            st.session_state['mode'] = st.session_state['mode_form']
        st.session_state['backward'] = "等待叫号"
        st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = "等待叫号"
        st.session_state['loop'] = False

    with st.form(key='change_mode_form'):
        st.warning("是否要修改充电模式？修改充电模式将重新排队")
        if st.session_state['mode'] == '快充':
            idx = 0
        else:
            idx = 1
        st.radio("修改充电模式 👇", ('快充', '慢充'), help="快充 (30 度/小时), 慢充 (7 度/小时)", index=idx,
                 key="mode_form")
        st.form_submit_button(label='确认修改', on_click=mode_form_callback)

    st.button("返回", on_click=return_on_click)

    backward("等待叫号")


def change_degree():
    st.markdown("#### 等待叫号")
    show_hao(st.session_state['wait'], st.session_state['mode'], st.session_state['degree'])

    def degree_form_callback():
        if st.session_state['degree'] == st.session_state['degree_form']:
            # st.warning("没有修改充电电量")
            st.session_state['warning_flag'] = True
            st.session_state['warning_info'] = "没有修改充电电量"
        else:
            # st.success(f"修改充电电量为:{st.session_state['degree_form']}")
            st.session_state['degree'] = st.session_state['degree_form']
        st.session_state['backward'] = "等待叫号"
        st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = "等待叫号"
        st.session_state['loop'] = False

    with st.form(key='change_degree_form'):
        st.info("修改充电模式不用重新排队。是否要修改充电电量？")
        st.slider('请求充电量 (度)', 0.0, st.session_state['capacity'], st.session_state['degree'], 0.1,
                  key="degree_form")
        st.form_submit_button(label='确认修改', on_click=degree_form_callback)

    st.button("返回", on_click=return_on_click)

    backward("等待叫号")


def cancel():
    st.markdown("#### 等待叫号")
    show_hao(st.session_state['wait'], st.session_state['mode'], st.session_state['degree'])

    def cancel_confirm_on_click():
        st.session_state['backward'] = "提交充电请求"
        st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = "等待叫号"
        st.session_state['loop'] = False

    st.warning("是否确认取消充电请求？取消充电请求本次排队号作废")
    st.button("确定取消", on_click=cancel_confirm_on_click)

    st.button("返回", on_click=return_on_click)

    backward("等待叫号")


def waiting_for_charging():
    st.markdown("#### 正在充电区等候")

    def begin_on_click():
        st.session_state['stage'] = "开始充电"

    def cancel_on_click():
        st.session_state['stage'] = "取消充电_充电区"
        st.session_state['loop'] = True

    st.button("取消充电", on_click=cancel_on_click)

    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1)
    else:
        st.balloons()
        st.write("您已经可以开始充电了！是否开始充电？")
        st.button("开始充电", on_click=begin_on_click)


def cancel_waiting_for_charging():
    st.markdown("#### 正在充电区等候")

    def cancel_confirm_on_click():
        st.session_state['backward'] = "提交充电请求"
        st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = "准备充电"
        st.session_state['loop'] = False

    st.warning("是否确认取消充电请求？取消充电请求本次排队作废")
    st.button("确定取消", on_click=cancel_confirm_on_click)

    st.button("返回", on_click=return_on_click)

    backward("准备充电")


def begin_charging():
    st.markdown("#### 正在充电中")

    def cancel_on_click():
        st.session_state['stage'] = "取消充电_充电区"
        st.session_state['loop'] = True

    st.button("结束充电", on_click=cancel_on_click)

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


def termiante_charging():
    st.markdown("#### 正在充电中")

    def cancel_confirm_on_click():
        st.session_state['backward'] = "提交充电请求"
        st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = "开始充电"
        st.session_state['loop'] = False

    st.warning("是否确认结束充电？结束充电将按照实际充电量收取费用")
    st.button("确定结束", on_click=cancel_confirm_on_click)

    st.button("返回", on_click=return_on_click)

    backward("开始充电")


def end():
    st.markdown("#### 结束充电并缴费")

    def pay_on_click():
        st.session_state['stage'] = "提交充电请求"

    st.button("确认支付", on_click=pay_on_click)


# 未登录阶段
if st.session_state['stage'] == '用户登录':
    user_login()

if st.session_state['stage'] == '用户注册':
    user_logon()

# 未提交充电请求阶段
if st.session_state['stage'] == '提交充电请求':
    commit_charging_request()

# 等待叫号阶段
if st.session_state['stage'] == '等待叫号':
    waiting()

if st.session_state['stage'] == "修改充电模式":
    change_mode()

if st.session_state['stage'] == "修改充电量":
    change_degree()

if st.session_state['stage'] == "取消充电":
    cancel()

if st.session_state['stage'] == "准备充电":
    waiting_for_charging()

if st.session_state['stage'] == "取消充电_充电区":
    cancel_waiting_for_charging()

if st.session_state['stage'] == "开始充电":
    begin_charging()

if st.session_state['stage'] == "结束充电":
    termiante_charging()

if st.session_state['stage'] == "结束充电并缴费":
    end()
