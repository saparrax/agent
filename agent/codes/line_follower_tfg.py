import math
import time
import os
from sensors_tfg import Sensors

class LineFollower:

    

    def __init__(self, car, sensors):
        REFERENCES = [200,200,200,200,200]
        self.car = car
        self.sensors = sensors
        self.references = REFERENCES

    def follow_line(self):
        while True:
            digital_list = self.sensors.read_digital_line(self.references)
	    turning_direction = self.car.get_turning_direction()
            car_stopped = self.car.is_car_stopped()

            if turning_direction == "left":
                if digital_list[0] or digital_list[1]:
                    digital_list[2] = 0
		    digital_list[3] = 0
                    digital_list[4] = 0
            elif turning_direction == "right":
                if digital_list[3] or digital_list[4]:
                    digital_list[2] = 0
		    digital_list[1] = 0
                    digital_list[0] = 0
            elif turning_direction == "straight":
                digital_list[0] = 0
		digital_list[4] = 0
            elif turning_direction == "emergency_stop" or turning_direction == "stop":
                digital_list = [0, 0, 0, 0, 0]
            else:
                time.sleep(0.01)

#            speed = 0
#	    angle = 0
#            if digital_list == [0,1,1,1,0] or digital_list == [0,0,1,0,0]:
#                self.car.set_speed(80)
#                self.car.set_angle(90)
#		speed = 80
#		angle = 90	
#            if digital_list == [0,1,1,0,0]:
#                self.car.set_speed(70)
#                self.car.set_angle(80)
#		speed = 70
#		angle = 80	
#            if digital_list == [0,0,1,1,0]:
#                self.car.set_speed(70)
#                self.car.set_angle(100)
#		speed = 70
#		angle = 100	
#            if digital_list == [1,1,1,0,0]:
#                self.car.set_speed(60)
#                self.car.set_angle(70)
#		speed = 60
#		angle = 70	
#            if digital_list == [0,0,1,1,1]:
#                self.car.set_speed(60)
#                self.car.set_angle(110)
#		speed = 60
#		angle = 110	
#            if digital_list == [1,1,0,0,0]:
#                self.car.set_speed(50)
#                self.car.set_angle(60)
#		speed = 50
#		angle = 60	
#            if digital_list == [0,0,0,1,1]:
#                self.car.set_speed(50)
#                self.car.set_angle(120)
#		speed = 50
#		angle = 120	
#            if digital_list == [0,1,0,0,0]:
#                self.car.set_speed(45)
#                self.car.set_angle(53)
#		speed = 45
#		angle = 53	
#            if digital_list == [0,0,0,1,0]:
#                self.car.set_speed(45)
#                self.car.set_angle(128)
#		speed = 45
#		angle = 128	
#            if digital_list == [1,0,0,0,0]:
#                self.car.set_speed(40)
#                self.car.set_angle(45)
#		speed = 40
# 		angle = 45	
#            if digital_list == [0,0,0,0,1]:
#                self.car.set_speed(40)
#                self.car.set_angle(135)
#		speed = 40
#		angle = 135	
	    if digital_list[2] == 1:
                self.car.set_speed_level(9)
                self.car.set_angle(90)
		angle=90
            if digital_list[3] == 1:
                self.car.set_speed_level(5)
                self.car.set_angle(108)
		angle=105
            if digital_list[4] == 1:
                self.car.set_speed_level(3)
                self.car.set_angle(130)
                angle=120
	    if digital_list[1] == 1:
                self.car.set_speed_level(5)
                self.car.set_angle(72)
	  	angle=75
	    if digital_list[0] == 1:
                self.car.set_speed_level(3)
                self.car.set_angle(50)
		angle=90
	    if digital_list == [1,0,0,0,0]:
		self.car.set_speed(30)
		self.car.set_angle(45)
	    if digital_list == [0,0,0,0,1]:
		self.car.set_speed(30)
		self.car.set_angle(135)
