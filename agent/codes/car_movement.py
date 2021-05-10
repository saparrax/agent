from picar import front_wheels, back_wheels
import random
import picar
import time


class CarMovement:

    DEFAULT_SPEED = 0
    DEFAULT_ANGLE = 90
    TURNING_DEGREES = 5
    SPEED_INCREMENT = 10
    MIN_SPEED = -80
    MAX_SPEED = 80
    MIN_ANGLE = 45
    MAX_ANGLE = 135
    DIRECTION_LEFT = "left"
    DIRECTION_RIGHT = "right"
    DIRECTION_STAIGHT = "straight"

    def __init__(self):
        picar.setup()
        self.is_stopped = False
        self.bw = back_wheels.Back_Wheels()
        self.fw = front_wheels.Front_Wheels()
        self.motor_speed = 0
        self.turning_direction = ""
        self.angle = self.DEFAULT_ANGLE

    def get_angle(self):
        return self.angle

    def set_angle(self, angle, calibration=False):
        self.angle = angle
        self.update_angle(calibration)

    def turn_right(self, level):
        self.angle += level*self.TURNING_DEGREES
        self.update_angle()

    def turn_left(self, level):
        self.angle -= level*self.TURNING_DEGREES
        self.update_angle()

    def update_speed(self):
        if not self.is_stopped:
            if self.motor_speed < self.MIN_SPEED:
                self.motor_speed = self.MIN_SPEED
            elif self.motor_speed > self.MAX_SPEED:
                self.motor_speed = self.MAX_SPEED

            if self.motor_speed < 0:
                self.bw.speed = -self.motor_speed
                self.bw.backward()
            else:
                self.bw.speed = self.motor_speed
                self.bw.forward()

    def update_angle(self, calibration=False):
        if calibration:
            if self.angle < self.MIN_ANGLE:
                self.angle = self.MIN_ANGLE
            elif self.angle > self.MAX_ANGLE:
                self.angle = self.MAX_ANGLE
            self.fw.turn(self.angle)
        elif not self.is_stopped and self.motor_speed != 0:
            if self.angle < self.MIN_ANGLE:
                self.angle = self.MIN_ANGLE
            elif self.angle > self.MAX_ANGLE:
                self.angle = self.MAX_ANGLE
            self.fw.turn(self.angle)

	def get_speed(self):
		return self.motor_speed

    def set_speed(self, speed):
        self.motor_speed = speed
        self.update_speed()

    def set_speed_level(self, speed_level):
        self.motor_speed = speed_level*self.SPEED_INCREMENT
        self.update_speed()

    def get_speed_level(self):
        return self.motor_speed/self.SPEED_INCREMENT

    def accelerate(self, level):
        self.motor_speed += level*self.SPEED_INCREMENT
        self.update_speed()

    def decelerate(self, level):
        self.motor_speed -= level*self.SPEED_INCREMENT
        self.update_speed()

    def brake(self):
        self.motor_speed = self.DEFAULT_SPEED
        self.bw.speed = self.motor_speed
        self.is_stopped = True

    def stop(self):
        self.set_angle(self.DEFAULT_ANGLE)
        self.is_stopped = True
        self.turning_direction = "stop"
        self.brake()

    def run(self):
        self.is_stopped = False
        self.update_speed()
        self.turning_direction = ""

    def is_car_stopped(self):
        return self.is_stopped

    def get_turning_direction(self):
        return self.turning_direction

    def left_corner(self):
        self.set_speed(50)
        self.turning_direction = self.DIRECTION_LEFT


    def right_corner(self):
        self.set_speed(50)
        self.turning_direction = self.DIRECTION_RIGHT


    def go_straight(self):
        self.turning_direction = self.DIRECTION_STAIGHT

    def emergency_stop(self):
        self.turning_direction = "emergency_stop"
        self.stop()
        time.sleep(4)
        self.turning_direction = ""

    def empty_action(self):
        self.turning_direction = ""
