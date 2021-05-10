import time
import json
from car_movement import CarMovement


try:
    car = CarMovement()
    car.set_angle(car.DEFAULT_ANGLE, calibration=True)
    time.sleep(1)
    car.set_angle(car.MIN_ANGLE, calibration=True)
    time.sleep(1)
    car.set_angle(car.DEFAULT_ANGLE, calibration=True)
    time.sleep(1)
    car.set_angle(car.MAX_ANGLE, calibration=True)
    time.sleep(1)
    car.set_angle(car.DEFAULT_ANGLE, calibration=True)
    time.sleep(1)
    car.set_speed(50)
    time.sleep(1)
    car.set_speed(-50)
    time.sleep(1)
    car.set_speed(0)
    print(json.dumps({"status": "success", "output": "Car wheels and motor calibrated successfully"}))
except Exception, e:
    print("ERROR:{}".format(e))
