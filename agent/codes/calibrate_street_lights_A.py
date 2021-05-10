from util import get_params
import socket
import json
import time
import sys



CALIBRATE_STREET_LIGHT = "calibrate_street_light"

def connect_socket(ip, port):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((ip, port))
        return s
    except:
        time.sleep(0.5)
        return connect_socket(ip, port)


try:
    params = get_params(sys.argv)
    street_light_ip = params["GESTION_FAROLAS_ip"]
    street_light_port = int(params["GESTION_FAROLAS_port"])
    s_street_light = connect_socket(street_light_ip, street_light_port)
    time.sleep(3)
    s_street_light.send(CALIBRATE_STREET_LIGHT.encode())
    message = s_street_light.recv(4096).decode()
    print(json.dumps({"message" : message}))
except Exception as e:
    print("ERROR:{}".format(e))
