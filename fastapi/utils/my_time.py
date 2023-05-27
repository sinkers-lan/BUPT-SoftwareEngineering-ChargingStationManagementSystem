import datetime
import time
import threading


class VirtualTime:
    def __init__(self):
        self.start_time = time.time()
        self.time_multiplier = 1000
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

        if not self.is_start:
            # 创建并启动后台线程
            self.thread = threading.Thread(target=update_virtual_time)
            self.thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
            self.thread.start()
            self.is_start = True

    def get_current_time(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        return self.current_virtual_time

    def get_current_datetime(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        dt = datetime.datetime.fromtimestamp(self.current_virtual_time)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 去除微秒后的后缀三位
        return formatted_time

    def accelerate(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        self.time_multiplier = 1000

    def moderate(self):
        if not self.is_start:
            raise Exception('Virtual time has not yet started')
        self.time_multiplier = 1


virtual_time = VirtualTime()


class VirtualTimeCallback:
    def __init__(self, virtual_time: VirtualTime, specified_time, callback):
        self.virtual_time = virtual_time
        self.specified_time = specified_time
        self.callback = callback

    def start(self):
        def check_time_and_callback():
            while True:
                current_virtual_time = self.virtual_time.get_current_time()
                if current_virtual_time >= self.specified_time:
                    self.callback()
                    break
                time.sleep(0.1)

        if not virtual_time.is_start:
            raise Exception('Virtual time has not yet started')
        self.thread = threading.Thread(target=check_time_and_callback)
        self.thread.start()


def start_timer(delay, callback):
    specified_time = virtual_time.get_current_time() + delay
    virtual_time_cb = VirtualTimeCallback(virtual_time, specified_time, callback)
    virtual_time_cb.start()
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
