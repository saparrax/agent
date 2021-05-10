import sys

from picar import front_wheels, back_wheels
import random
import picar
import time

def stop():
    bw = back_wheels.Back_Wheels()
    fw = front_wheels.Front_Wheels()
    bw.speed=0
    fw.turn(90)
    print ("Stop")
    sys.exit(1)


if __name__ == "__main__":
    stop()






