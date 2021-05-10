import json
import time
from car_movement import CarMovement
from sensors import Sensors
from line_follower import LineFollower


try:
	car = CarMovement()
	sensors = Sensors()
	line_follower = LineFollower(car, sensors)
	line_follower.calibration(wheels=True)
	print(json.dumps({"message" : "Line sensor calibrated successfully"}))
except Exception, e:
	print("ERROR:{}".format(e))
