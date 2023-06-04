import re
from enum import Enum

import streamlit as st
import time

from utils import utils


class Stage(Enum):
    LOGIN = "用户登录"
    REGISTER = "用户注册"
    SUBMIT = "提交充电请求"
    WAIT = "等待叫号"
    CHANGE_MODE = "更改充电模式"
    CHANGE_AMOUNT = "更改充电量"
    CANCEL_WAIT = "取消等待叫号"
    WAIT_FOR_CHARGE = "等待充电"
    CANCEL_WAIT_FOR_CHARGE = "取消等待充电"
    ALLOW_CHARGE = "允许充电"
    CANCEL_ALLOW_CHARGE = "取消允许充电"
    CHARGE = "开始充电"
    CANCEL_CHARGE = "结束充电"
    PAY = "缴费"


# 设置全局变量
if 'stage' not in st.session_state:
    st.session_state['stage'] = Stage.LOGIN.value
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
if 'initial_queue_len' not in st.session_state:
    st.session_state['initial_queue_len'] = None
if 'your_position' not in st.session_state:
    st.session_state['your_position'] = None
if 'hao' not in st.session_state:
    st.session_state['hao'] = None
if "token" not in st.session_state:
    st.session_state['token'] = None
if "backward" not in st.session_state:
    st.session_state['backward'] = Stage.SUBMIT.value
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
if st.session_state['stage'] == Stage.LOGIN.value or st.session_state['stage'] == Stage.REGISTER.value:
    st.sidebar.warning("用户登录")
    st.sidebar.info("提交充电请求")
    st.sidebar.info("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == Stage.SUBMIT.value:
    st.sidebar.success("用户登录")
    st.sidebar.warning("提交充电请求")
    st.sidebar.info("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == Stage.WAIT.value or \
        st.session_state['stage'] == Stage.CHANGE_MODE.value or \
        st.session_state['stage'] == Stage.CHANGE_AMOUNT.value or \
        st.session_state['stage'] == Stage.CANCEL_WAIT.value:
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.warning("等待叫号")
    st.sidebar.info("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == Stage.WAIT_FOR_CHARGE.value \
        or st.session_state['stage'] == Stage.ALLOW_CHARGE.value \
        or st.session_state['stage'] == Stage.CHARGE.value \
        or st.session_state['stage'] == Stage.CANCEL_WAIT_FOR_CHARGE.value \
        or st.session_state['stage'] == Stage.CANCEL_ALLOW_CHARGE.value or \
        st.session_state['stage'] == Stage.CANCEL_CHARGE.value:
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.success("等待叫号")
    st.sidebar.warning("开始充电")
    st.sidebar.info("结束充电并缴费")
if st.session_state['stage'] == Stage.PAY.value:
    st.sidebar.success("用户登录")
    st.sidebar.success("提交充电请求")
    st.sidebar.success("等待叫号")
    st.sidebar.success("开始充电")
    st.sidebar.warning("结束充电并缴费")


# st.write(st.session_state['stage'])


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


def login():
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户登录")
    phone = st.text_input("手机号")
    password = st.text_input("密码", type="password")

    def login_on_click(args):
        if args == "logon":
            st.session_state['stage'] = Stage.REGISTER.value
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
                st.session_state['stage'] = Stage.SUBMIT.value
            else:
                st.error(data['message'])
            pass

    col1, col2 = st.columns(2)
    with col1:
        st.button("登录", on_click=login_on_click, args=("login",), use_container_width=True)
    with col2:
        st.button("注册", on_click=login_on_click, args=("logon",), use_container_width=True)


if st.session_state['stage'] == Stage.LOGIN.value:
    login()


def register():
    st.markdown("## 智能充电桩充电系统 🎈")
    st.markdown("#### 用户注册")
    phone = st.text_input("手机号")
    password = st.text_input("密码", type="password")
    car = st.text_input("车牌号")
    capacity = st.slider('电车电池总容量 (度)', 15.0, 60.0, 45.0, 0.1, key="capacity_form")

    def login_on_click(args):
        print(args)
        if args == "login":
            st.session_state['stage'] = Stage.LOGIN.value
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
        data = utils.post(my_json=my_json, path="/user/register")
        if data['code'] == 1:
            st.session_state['user'] = phone
            st.session_state['token'] = data['data']['token']
            st.session_state['capacity'] = capacity
            st.session_state['car'] = car
            st.session_state['stage'] = Stage.SUBMIT.value
        else:
            st.error(data['message'])
        pass

    col1, col2 = st.columns(2)
    with col1:
        st.button("登录", on_click=login_on_click, args=("login",), use_container_width=True)
    with col2:
        st.button("注册", on_click=login_on_click, args=("logon",), use_container_width=True)


if st.session_state['stage'] == Stage.REGISTER.value:
    register()


def submit_charging_request():
    st.markdown("### 提交充电请求")
    st.markdown("----")
    show_info()
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
        return 0
    if data_['data']['car_state'] == '处于充电区':
        st.session_state['stage'] = Stage.WAIT_FOR_CHARGE.value
        st.experimental_rerun()
    elif data_['data']['car_state'] == '允许充电':
        st.session_state['stage'] = Stage.ALLOW_CHARGE.value
        st.experimental_rerun()
    elif data_['data']['car_state'] == '处于等候区':
        st.session_state['stage'] = Stage.WAIT.value
        st.experimental_rerun()
    elif data_['data']['car_state'] == '正在充电':
        st.session_state['stage'] = Stage.CHARGE.value
        st.experimental_rerun()
    elif data_['data']['car_state'] == "结束充电":
        st.session_state['stage'] = Stage.PAY.value
        st.experimental_rerun()
    elif data_['data']['car_state'] == "空闲":
        pass
    else:
        st.error("未知状态：" + data_['data']['car_state'])
        return 0
    st.write("")
    st.session_state['degree'] = st.slider('请求充电量 (度)', 0.0, st.session_state['capacity'], 0.0, 0.1)
    st.write("")
    st.session_state['mode'] = st.radio("充电模式", ('快充', '慢充'), help="快充 (30 度/小时), 慢充 (7 度/小时)",
                                        horizontal=True)
    st.write("")
    st.info(f"请确认您要提交的充电请求：{st.session_state['mode']} {st.session_state['degree']} (度)")

    def confirm_on_click():
        if st.session_state['degree'] == 0:
            st.error("不能提交0度的充电请求")
        else:
            data = {
                "car_id": st.session_state['car'],
                "request_amount": st.session_state['degree'],
                "request_mode": "F" if st.session_state['mode'] == '快充' else "T"
            }
            data_ = utils.post(data, path="/user/chargingRequest", token=st.session_state['token'])
            if data_['code'] == 1:
                if data_['data']['car_state'] == '处于等候区':
                    st.session_state['stage'] = Stage.WAIT.value
                elif data_['data']['car_state'] == '处于充电区':
                    st.session_state['stage'] = Stage.WAIT_FOR_CHARGE.value
                elif data_['data']['car_state'] == '允许充电':
                    st.session_state['stage'] = Stage.ALLOW_CHARGE.value
                st.session_state['hao'] = data_['data']['queue_num']
            else:
                st.error(data_['message'])

    st.button("提交充电请求", on_click=confirm_on_click, use_container_width=True)


if st.session_state['stage'] == Stage.SUBMIT.value:
    submit_charging_request()


def show_hao():
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
        return 0
    st.session_state['hao'] = data_['data']['queue_num']
    st.session_state['mode'] = '快充' if data_['data']['request_mode'] == 'F' else '慢充'
    st.session_state['degree'] = data_['data']['request_amount']
    if data_['data']['pile_id'] is not None:
        st.write("排队号:", st.session_state['hao'], "，充电模式:", st.session_state['mode'],
                 "，请求充电量:", st.session_state['degree'], "度", "，充电桩号:", data_['data']['pile_id'])
    else:
        st.write("您的排队号码是:", st.session_state['hao'], "，您的充电模式:", st.session_state['mode'],
                 "，您的请求充电量：",
                 st.session_state['degree'], "度")


def backward(default_stage):
    st.write("")
    with st.empty():
        if st.session_state['loop']:
            for seconds in range(0, 20):
                st.write(f"20秒后超时返回  ⏳ {20 - seconds}")
                time.sleep(1)
            else:
                st.write("操作超时")
                st.session_state['stage'] = default_stage
                st.experimental_rerun()
        else:
            st.session_state['stage'] = st.session_state['backward']
            st.experimental_rerun()


def get_front_num(now_state: str):
    data = {
        "car_id": st.session_state['car']
    }
    data_ = utils.post(data, path="/user/queryCarState", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
        return 0
    if data_['data']['car_state'] == '处于充电区':
        st.session_state['stage'] = Stage.WAIT_FOR_CHARGE.value
    elif data_['data']['car_state'] == '允许充电':
        st.session_state['stage'] = Stage.ALLOW_CHARGE.value
    elif data_['data']['car_state'] == '处于等候区':
        st.session_state['stage'] = Stage.WAIT.value
    elif data_['data']['car_state'] == '结束充电':
        st.session_state['stage'] = Stage.PAY.value
    elif data_['data']['car_state'] == "空闲":
        st.session_state['stage'] = Stage.SUBMIT.value
    elif data_['data']['car_state'] == "正在充电":
        st.session_state['stage'] = Stage.CHARGE.value
    else:
        st.error("未知状态", data_['data']['car_state'])
    if now_state != st.session_state['stage']:
        st.experimental_rerun()
    car_position = data_['data']['car_position']
    # 前车等待数量
    return car_position - 1


def wait():
    st.markdown("### 等待叫号")
    st.markdown("----")
    show_info()
    # st.write("")
    show_hao()

    def change_mode_on_click():
        st.session_state['stage'] = Stage.CHANGE_MODE.value
        st.session_state['loop'] = True

    def change_degree_on_click():
        st.session_state['stage'] = Stage.CHANGE_AMOUNT.value
        st.session_state['loop'] = True

    def cancel_on_click():
        st.session_state['stage'] = Stage.CANCEL_WAIT.value
        st.session_state['loop'] = True

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("修改充电模式", on_click=change_mode_on_click, use_container_width=True)
    with col2:
        st.button("修改充电量", on_click=change_degree_on_click, use_container_width=True)
    with col3:
        st.button("取消本次充电", on_click=cancel_on_click, use_container_width=True)

    st.write("")
    st.markdown("##### 等待进度")

    st.session_state['initial_queue_len'] = get_front_num(st.session_state['stage'])

    my_bar = st.progress(0)
    while True:
        front_num = get_front_num(st.session_state['stage'])
        if front_num == 0:
            my_bar.progress(0.99, text=f"前车等待数量: 0")
        else:
            percent = (st.session_state['initial_queue_len'] - front_num) / st.session_state['initial_queue_len']
            my_bar.progress(percent, text=f"前车等待数量: {front_num}")
        time.sleep(1)


if st.session_state['stage'] == Stage.WAIT.value:
    wait()


def change_mode():
    st.markdown("### 等待叫号")
    st.markdown("----")
    show_info()
    show_hao()

    def mode_form_callback():
        if st.session_state['mode'] == st.session_state['mode_form']:
            # st.warning("没有修改充电模式")
            st.session_state['warning_flag'] = True
            st.session_state['warning_info'] = "没有修改充电模式"
        else:
            data = {
                "car_id": st.session_state['car'],
                "request_mode": st.session_state['mode_form']
            }
            data_ = utils.post(data, path="/user/changeChargingMode", token=st.session_state['token'])
            if data_['code'] == 0:
                st.session_state['error_flag'] = True
                st.session_state['error_info'] = data_['message']
            else:
                st.session_state['success_flag'] = True
                st.session_state['success_info'] = "修改充电模式成功"
                st.session_state['mode'] = st.session_state['mode_form']
                st.session_state['backward'] = Stage.WAIT.value
                st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.WAIT.value
        st.session_state['loop'] = False

    with st.form(key='change_mode_form'):
        st.warning("是否要修改充电模式？修改充电模式将重新排队")
        if st.session_state['mode'] == '快充':
            idx = 0
        else:
            idx = 1
        st.radio("修改充电模式", ('快充', '慢充'), help="快充 (30 度/小时), 慢充 (7 度/小时)", index=idx,
                 key="mode_form")
        st.form_submit_button(label='确认修改', on_click=mode_form_callback, use_container_width=True)

    st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.WAIT.value)


if st.session_state['stage'] == Stage.CHANGE_MODE.value:
    change_mode()


def change_degree():
    st.markdown("### 等待叫号")
    st.markdown("----")
    show_info()
    show_hao()

    def degree_form_callback():
        if st.session_state['degree'] == st.session_state['degree_form']:
            # st.warning("没有修改充电电量")
            st.session_state['warning_flag'] = True
            st.session_state['warning_info'] = "没有修改充电电量"
        else:
            data = {
                "car_id": st.session_state['car'],
                "request_amount": st.session_state['degree_form']
            }
            data_ = utils.post(data, path="/user/changeChargingAmount", token=st.session_state['token'])
            if data_['code'] == 0:
                st.session_state['error_flag'] = True
                st.session_state['error_info'] = data_['message']
            else:
                st.session_state['success_flag'] = True
                st.session_state['success_info'] = "修改充电电量成功"
                st.session_state['degree'] = st.session_state['degree_form']
                st.session_state['backward'] = Stage.WAIT.value
                st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.WAIT.value
        st.session_state['loop'] = False

    with st.form(key='change_degree_form'):
        st.info("修改充电模式不用重新排队。是否要修改充电电量？")
        st.slider('请求充电量 (度)', 0.0, st.session_state['capacity'], st.session_state['degree'], 0.1,
                  key="degree_form")
        st.form_submit_button(label='确认修改', on_click=degree_form_callback, use_container_width=True)

    st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.WAIT.value)


if st.session_state['stage'] == Stage.CHANGE_AMOUNT.value:
    change_degree()


def cancel_wait():
    st.markdown("### 等待叫号")
    st.markdown("----")
    show_info()
    show_hao()

    def cancel_confirm_on_click():
        data = {
            "car_id": st.session_state['car']
        }
        data_ = utils.post(data, path="/user/endCharging", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "取消充电请求成功"
            st.session_state['backward'] = Stage.SUBMIT.value
            st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.WAIT.value
        st.session_state['loop'] = False

    st.warning("是否确认取消充电请求？取消充电请求本次排队号作废")
    col1, col2 = st.columns(2)
    with col1:
        st.button("确定取消", on_click=cancel_confirm_on_click, use_container_width=True)
    with col2:
        st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.WAIT.value)


if st.session_state['stage'] == Stage.CANCEL_WAIT.value:
    cancel_wait()


def wait_for_charge():
    st.markdown("### 正在充电区等候")
    st.markdown("----")
    show_info()
    show_hao()

    def cancel_on_click():
        st.session_state['stage'] = Stage.CANCEL_WAIT_FOR_CHARGE.value
        st.session_state['loop'] = True

    st.button("取消充电", on_click=cancel_on_click, use_container_width=True)

    st.session_state['initial_queue_len'] = get_front_num(st.session_state['stage'])()

    my_bar = st.progress(0)
    flag = True
    while flag:
        front_num = get_front_num(st.session_state['stage'])()
        if front_num == 0:
            my_bar.progress(1.0, text=f"前车等待数量: 0")
        else:
            percent = (st.session_state['initial_queue_len'] - front_num) / st.session_state['initial_queue_len']
            my_bar.progress(percent, text=f"前车等待数量: {front_num}")
        time.sleep(10)


if st.session_state['stage'] == Stage.WAIT_FOR_CHARGE.value:
    wait_for_charge()


def cancel_wait_for_charge():
    st.markdown("### 正在充电区等候")
    st.markdown("----")
    show_info()

    def cancel_confirm_on_click():
        data = {
            "car_id": st.session_state['car']
        }
        data_ = utils.post(data, path="/user/endCharging", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "取消充电请求成功"
            st.session_state['backward'] = Stage.SUBMIT.value
            st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.WAIT_FOR_CHARGE.value
        st.session_state['loop'] = False

    st.warning("是否确认取消充电请求？取消充电请求本次排队作废")
    col1, col2 = st.columns(2)
    with col1:
        st.button("确定取消", on_click=cancel_confirm_on_click, use_container_width=True)
    with col2:
        st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.WAIT_FOR_CHARGE.value)


if st.session_state['stage'] == Stage.CANCEL_WAIT_FOR_CHARGE.value:
    cancel_wait_for_charge()


def allow_charge():
    st.markdown("### 允许充电")
    st.markdown("----")
    st.balloons()
    show_info()
    show_hao()

    def begin_on_click():
        data = {
            "car_id": st.session_state['car']
        }
        data_ = utils.post(data, path="/user/beginCharging", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "开始充电成功"
            st.session_state['stage'] = Stage.CHARGE.value
            # 计算预计充电时间
            mode = st.session_state['mode']
            degree = st.session_state['degree']
            power = 30.0 if mode == "快充" else 7.0
            during = degree / power
            st.session_state['during'] = during
            st.session_state['end_time'] = utils.format_datetime_s(time.time() + during * 3600)

    st.write("您已经可以开始充电了！是否开始充电？")
    col1, col2 = st.columns(2)
    with col1:
        st.button("开始充电", on_click=begin_on_click, use_container_width=True)

    def cancel_on_click():
        st.session_state['stage'] = Stage.CANCEL_ALLOW_CHARGE.value
        st.session_state['loop'] = True

    with col2:
        st.button("取消充电", on_click=cancel_on_click, use_container_width=True)

    while True:
        get_front_num(st.session_state['stage'])
        time.sleep(2)


if st.session_state['stage'] == Stage.ALLOW_CHARGE.value:
    allow_charge()


def cancel_allow_charge():
    st.markdown("### 允许充电")
    st.markdown("----")
    show_info()

    def cancel_confirm_on_click():
        data = {
            "car_id": st.session_state['car']
        }
        data_ = utils.post(data, path="/user/endCharging", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "取消充电请求成功"
            st.session_state['backward'] = Stage.SUBMIT.value
            st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.ALLOW_CHARGE.value
        st.session_state['loop'] = False

    st.warning("是否确认取消充电请求？取消充电请求本次排队作废")
    col1, col2 = st.columns(2)
    with col1:
        st.button("确定取消", on_click=cancel_confirm_on_click, use_container_width=True)
    with col2:
        st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.ALLOW_CHARGE.value)


if st.session_state['stage'] == Stage.CANCEL_ALLOW_CHARGE.value:
    cancel_allow_charge()


def begin_charge():
    st.markdown("### 正在充电中")
    st.markdown("----")
    show_info()

    def cancel_on_click():
        st.session_state['stage'] = Stage.CANCEL_CHARGE.value
        st.session_state['loop'] = True

    st.button("结束充电", on_click=cancel_on_click, use_container_width=True)

    # st.markdown("#### 充电进度")
    st.write("预计充电时间为：", round(st.session_state['during'], 2), "小时")
    st.write("预计充电结束时间为：", st.session_state['end_time'])
    with st.spinner('正在充电中...'):
        while True:
            get_front_num(st.session_state['stage'])
            time.sleep(1)


if st.session_state['stage'] == Stage.CHARGE.value:
    begin_charge()


def cancel_charge():
    st.markdown("### 正在充电中")
    st.markdown("----")
    show_info()

    def cancel_confirm_on_click():
        data = {
            "car_id": st.session_state['car']
        }
        data_ = utils.post(data, path="/user/endCharging", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "取消充电请求成功"
            st.session_state['backward'] = Stage.PAY.value
            st.session_state['loop'] = False

    def return_on_click():
        st.session_state['backward'] = Stage.CHARGE.value
        st.session_state['loop'] = False

    st.warning("是否确认结束充电？结束充电将按照实际充电量收取费用")
    col1, col2 = st.columns(2)
    with col1:
        st.button("确定结束", on_click=cancel_confirm_on_click, use_container_width=True)
    with col2:
        st.button("返回", on_click=return_on_click, use_container_width=True)

    backward(Stage.CHARGE.value)


if st.session_state['stage'] == Stage.CANCEL_CHARGE.value:
    cancel_charge()


def pay():
    st.markdown("### 结束充电并缴费")
    st.markdown("---")
    show_info()

    data = {
        "car_id": st.session_state['car']
    }
    _data = utils.post(data, path="/user/getChargingState", token=st.session_state['token'])
    st.session_state['bill_id'] = _data['data']['bill_id']
    bill_details = _data['data']
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("**账单流水号**：")
        st.write("**车牌号**：")
        st.write("**账单日期**：")
        st.write("**充电起始时间**：")
        st.write("**充电结束时间**：")
        st.write("**充电量**：")
        st.write("**充电总时长**：")
        st.write("**充电费用**：")
        st.write("**服务费用**：")
        st.write("**总费用**：")
    with col2:
        st.write(bill_details['bill_id'])
        st.write(bill_details['car_id'])
        st.write(bill_details['bill_date'])
        st.write(bill_details['start_time'])
        st.write(bill_details['end_time'])
        st.write(bill_details['charge_amount'], '度')
        st.write(bill_details['charge_duration'], '时')
        st.write(bill_details['total_charge_fee'], '元')
        st.write(bill_details['total_service_fee'], '元')
        st.write(bill_details['total_fee'], '元')

    def pay_on_click():
        data = {
            "bill_id": st.session_state['bill_id']
        }
        data_ = utils.post(data, path="/user/getPayBill", token=st.session_state['token'])
        if data_['code'] == 0:
            st.session_state['error_flag'] = True
            st.session_state['error_info'] = data_['message']
        else:
            st.session_state['success_flag'] = True
            st.session_state['success_info'] = "支付成功！充电完成，欢迎下次使用"
            st.session_state['stage'] = Stage.SUBMIT.value

    st.button("确认支付", on_click=pay_on_click, use_container_width=True)


if st.session_state['stage'] == Stage.PAY.value:
    pay()
