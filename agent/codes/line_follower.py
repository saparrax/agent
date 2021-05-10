import math
import time
import os
from sensors import Sensors

class LineFollower:

    CALIBRATION_FILE = '/etc/agent/config/calibration.config'

    def __init__(self, car, sensors):
        self.references = [-1,-1,-1,-1,-1]
        self.car = car
        self.sensors = sensors
        if not self.is_calibrated():
            self.calibration()
        else:
            self.load_calibration()

    def load_calibration(self):
        i = 0
        file = open(self.CALIBRATION_FILE, 'r')
        content = file.readlines()
        for c in content:
            self.references[i] = int(c.rstrip())
            i += 1
        file.close()
        file = open(self.CALIBRATION_FILE, 'w')
        for r in self.references:
            file.write(str(r) + '\n')
        file.close()

    def is_calibrated(self):
        return os.path.isfile(self.CALIBRATION_FILE)

    def calculate_reference(self, white_reference, black_reference):
        for i in range(0, 5):
            self.references[i] = (white_reference[i] - black_reference[i])/2 + black_reference[i]
        file = open(self.CALIBRATION_FILE, 'w+')
        for r in self.references:
            file.write(str(r) + '\n')
        file.close()


    def calibration(self, wheels=False):
        if wheels:
            self.car.set_angle(self.car.DEFAULT_ANGLE, wheels)
            time.sleep(1)
            self.car.set_angle(self.car.MIN_ANGLE, wheels)
        black_reference = self.sensors.test_color_line()
        if wheels: self.car.set_angle(self.car.MAX_ANGLE, wheels)
        white_reference = self.sensors.test_color_line()
        if wheels: self.car.set_angle(self.car.DEFAULT_ANGLE, wheels)
        self.calculate_reference(white_reference, black_reference)

    def follow_line(self):
        while True:
            digital_list = self.sensors.read_digital_line(self.references)
            turning_direction = self.car.get_turning_direction()
            car_stopped = self.car.is_car_stopped()

            if turning_direction == "left":
                if digital_list[0] or digital_list[1]:
                    digital_list[2] = digital_list[3] = 0
                digital_list[4] = 0
            elif turning_direction == "right":
                if digital_list[3] or digital_list[4]:
                    digital_list[2] = digital_list[1] = 0
                digital_list[0] = 0
            elif turning_direction == "straight":
                digital_list[0] = digital_list[4] = 0
            elif turning_direction == "emergency_stop" or turning_direction == "stop":
                digital_list = [0, 0, 0, 0, 0]
            else:
                time.sleep(0.01)

            if digital_list[0] == 1:
                self.car.set_speed_level(5)
                self.car.set_angle(60)
            if digital_list[1] == 1:
                self.car.set_speed_level(7)
                self.car.set_angle(75)
            if digital_list[2] == 1:
                self.car.set_speed_level(9)
                self.car.set_angle(90)
            if digital_list[3] == 1:
                self.car.set_speed_level(7)
                self.car.set_angle(105)
            if digital_list[4] == 1:
                self.car.set_speed_level(5)
                self.car.set_angle(120)
