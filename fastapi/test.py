from utils.my_time import virtual_time
from service.dispatch import dispatch

virtual_time.start()
dispatch.new_car_come(1, "京JG2431", "快充", 1.0)

