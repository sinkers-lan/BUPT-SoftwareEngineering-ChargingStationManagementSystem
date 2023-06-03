import datetime
import time
import threading
from typing import Tuple


class VirtualTime:
    def __init__(self):
        self.start_time = time.time()
        self.time_multiplier = 1
        self.current_virtual_time = time.time()
        self.is_start = False

    def start(self):
        # 在后台线程中更新虚拟时间
        def update_virtual_time():
            while True:
                elapsed_time = time.time() - self.start_time
                virtual_elapsed_time = elapsed_time * self.time_multiplier
                self.current_virtual_time = self.start_time + virtual_elapsed_time
                time.sleep(0.1)  # 调整更新间隔
                # print(self.get_current_datetime())

        if not self.is_start:
            # 创建并启动后台线程
            self.thread = threading.Thread(target=update_virtual_time)
            self.thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
            self.thread.start()
            self.is_start = True
            print("虚拟时间已启动")

    def get_current_time(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        return self.current_virtual_time

    def get_current_datetime(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        dt = datetime.datetime.fromtimestamp(self.current_virtual_time)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]  # 去除微秒后的后缀4位
        return formatted_time

    def get_current_date(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        dt = datetime.datetime.fromtimestamp(self.current_virtual_time)
        formatted_time = dt.strftime("%Y-%m-%d")
        return formatted_time

    def accelerate(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        self.time_multiplier = 100

    def moderate(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        self.time_multiplier = 1


virtual_time = VirtualTime()


class VirtualTimer:
    def __init__(self, virtual_time: VirtualTime, specified_time, callback, args: Tuple):
        self.virtual_time = virtual_time
        self.specified_time = specified_time
        self.callback = callback
        self.args = args
        self.running = False

    def start(self):
        def check_time_and_callback():
            while self.running:
                current_virtual_time = self.virtual_time.get_current_time()
                if current_virtual_time >= self.specified_time:
                    print("计时器到时")
                    self.callback(*self.args)
                    break
                time.sleep(0.1)

        if not virtual_time.is_start:
            raise Exception('Virtual time has not yet started')
        self.running = True
        self.thread = threading.Thread(target=check_time_and_callback, daemon=True, name='timer')
        self.thread.start()
        print("定时器已启动")

    def terminate(self):
        self.running = False


def start_timer(delay, callback, args):
    specified_time = virtual_time.get_current_time() + delay
    virtual_timer = VirtualTimer(virtual_time, specified_time, callback, args)
    virtual_timer.start()
    return virtual_timer
# if __name__ == "__main__":
#     virtual_time.start()
#     virtual_time.moderate()
#     while True:
#         current_virtual_time = virtual_time.get_current_time()
#         print("Virtual time:", current_virtual_time)
#         # 在这里进行其他操作
#
#         # 控制程序的运行速度
#         time.sleep(1)
