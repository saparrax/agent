import Ultrasonic_Avoidance
import serial
import smbus
import time
import math


class Sensors():

    pin_address = 0x11

    def __init__(self):
        self.UA = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
        self.bus = smbus.SMBus(1)
        self.arduino = serial.Serial('/dev/ttyACM0', baudrate=9600)


    def read_raw_line(self):
        for i in range(0, 5):
            try:
                raw_result = self.bus.read_i2c_block_data(self.pin_address, 0, 10)
                Connection_OK = True
                break
            except:
                Connection_OK = False
        if Connection_OK:
            return raw_result
        else:
            # print "Error accessing %2X" % self.pin_address
            return False


    def read_analog_line(self):
        raw_result = self.read_raw_line()
        if raw_result:
            analog_result = [0, 0, 0, 0, 0]
            for i in range(0, 5):
                high_byte = raw_result[i*2] << 8
                low_byte = raw_result[i*2+1]
                analog_result[i] = high_byte + low_byte
            return analog_result

    def valid_data_line(self, data):
        if data is not None:
            for element in data:
                if element < 0 or element > 2000:
                    return False
                return True
        else:
            # print "es none"
            pass

    def get_average_line(self, mount):
        if not isinstance(mount, int):
            raise ValueError("Mount must be interger")
        average = [0, 0, 0, 0, 0]
        lt_list = [[], [], [], [], []]
        times = 1
        while times <= 5:
            lt = self.read_analog_line()
            if self.valid_data_line(lt):
                # print "      time"+str(times)+": "+str(lt)
                for lt_id in range(0, 5):
                    lt_list[lt_id].append(lt[lt_id])
                times += 1

        for lt_id in range(0, 5):
            average[lt_id] = int(math.fsum(lt_list[lt_id])/mount)
        return average

    def test_color_line(self):
        for i in range(5, 0, -1):
            # print "    Test in :" + str(i)
            time.sleep(1)
        # print "    starting  Test..."
        time.sleep(1)
        return self.get_average_line(5)

    def read_digital_line(self, line_references):
        lt = self.read_analog_line()
        digital_list = []
        if self.valid_data_line(lt):
            for i in range(0, 5):
                if lt[i] < line_references[i]:
                    digital_list.append(0)
                elif lt[i] > line_references[i]:
                    digital_list.append(1)
                else:
                    digital_list.append(-1)
        else:
            digital_list = [0,0,0,0,0]
	return digital_list

    def read_distance(self):
        distance = self.UA.get_distance()
        while distance == -1:
            distance = self.UA.get_distance()
        return distance

    def read_RFID(self):
        c = ""
        text = ""
        while c != '\n':
            if self.arduino.inWaiting() > 0:
                c = self.arduino.read(1)
                text += c
        return text.strip()
