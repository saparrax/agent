import time
import json
from car_movement import CarMovement
from sensors_tfg import Sensors


try:
	car = CarMovement()
	sensors = Sensors()
	car.set_angle(car.DEFAULT_ANGLE)
	distance = 9999
	while distance > 10 and distance != -1:
		distance = sensors.read_distance()
	car.set_speed(-50)
	time.sleep(0.5)
	car.set_speed(0)
	print(json.dumps({"status": "success", "output": "Ultrasonic Sensor calibrated successfully"}))
except Exception, e:
	print("ERROR:{}".format(e))
