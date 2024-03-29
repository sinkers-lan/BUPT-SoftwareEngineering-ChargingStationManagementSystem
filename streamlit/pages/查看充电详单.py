from utils import utils
import streamlit as st


def get_total_bill(date=None):
    data = {
        "car_id": st.session_state['car'],
        "bill_date": date.strftime("%Y-%m-%d") if date else None
    }
    data_ = utils.post(data, path="/user/getTotalBill", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
    my_list = data_.get('data')
    return my_list['bill_list']


def get_detail_bill(bill_id):
    data = {
        "bill_id": bill_id
    }
    data_ = utils.post(data, path="/user/getDetailBill", token=st.session_state['token'])
    # st.write("data", data_)
    if data_['code'] == 0:
        st.error(data_['message'])
    return data_.get('data', {})


def get_pay_bill(bill_id):
    if "bill_id" is None:
        st.warning("请先获取账单")
        return
    data = {
        "bill_id": bill_id
    }
    data_ = utils.post(data, path="/user/getPayBill", token=st.session_state['token'])
    if data_['code'] == 0:
        st.error(data_['message'])
    else:
        st.success("支付成功")


# 设置页面标题和布局
st.markdown('### 电车充电账单信息')
st.markdown('---')

if "stage" not in st.session_state or st.session_state['stage'] == "用户登录" or st.session_state[
    'stage'] == "用户注册":
    st.write("请先登录")
    st.stop()

# 创建表格来展示账单摘要信息
show_all = st.checkbox('显示所有账单')
st.date_input('选择日期', key='date', help='选择查看指定日期的账单', disabled=show_all)
if show_all:
    all_bills = get_total_bill()
else:
    all_bills = get_total_bill(st.session_state['date'])

st.markdown('---')

if len(all_bills) == 0 or all_bills is None:
    st.warning('没有查到账单信息')
    st.stop()
for bill in all_bills:
    st.write('**账单ID:**', bill['bill_id'])
    col1, col2 = st.columns(2)
    with col1:
        st.write('**车牌号:**', bill['car_id'])
        st.write('**账单日期:**', bill['bill_date'])
        st.write('**总费用:**', round(bill['total_fee'], 2), '元')
    with col2:
        st.write('**充电开始时间:**', bill['start_time'])
        st.write('**充电结束时间:**', bill['end_time'])
        st.write('**支付状态:**', '已支付' if bill['pay_state'] == 1 else '未支付')
    st.write('---')

# 添加账单详情的展示
selected_bill_id = st.selectbox('选择要查看的账单ID', [bill['bill_id'] for bill in all_bills])

# 获取选中账单的详情信息
bill_details = get_detail_bill(selected_bill_id)

# 显示选中账单的详情信息
if bill_details:
    # st.markdown('##### 账单详情')
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
        st.write("**支付状态**：")
    with col2:
        st.write(bill_details['bill_id'])
        st.write(bill_details['car_id'])
        st.write(bill_details['bill_date'])
        st.write(bill_details['start_time'])
        st.write(bill_details['end_time'])
        st.write(round(bill_details['charge_amount'], 2), '度')
        hour, mint, sec = utils.get_hour_min_sec(bill_details['charge_duration'] * 3600)
        st.write(str(hour), '时', str(mint), '分', str(sec), '秒')
        # st.write(bill_details['charge_duration'])
        st.write(round(bill_details['total_charge_fee'], 2), '元')
        st.write(round(bill_details['total_service_fee'], 2), '元')
        st.write(round(bill_details['total_fee'], 2), '元')
        st.write('已支付' if bill_details['pay_state'] == 1 else '未支付')
    if bill_details['pay_state'] == 0:
        st.button('支付', on_click=get_pay_bill, args=(bill_details['bill_id'],), use_container_width=True)
else:
    st.warning('没有找到账单详情信息')
