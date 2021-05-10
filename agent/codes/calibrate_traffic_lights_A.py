from util import get_params
import socket
import json
import time
import sys



CALIBRATE_TRAFFIC_LIGHT = "calibrate_traffic_light"

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
    traffic_light_ip = params["GESTION_SEMAFOROS_ip"]
    traffic_light_port = int(params["GESTION_SEMAFOROS_port"])
    s_traffic_light = connect_socket(traffic_light_ip, traffic_light_port)
    time.sleep(3)
    s_traffic_light.send(CALIBRATE_TRAFFIC_LIGHT.encode())
    message = s_traffic_light.recv(4096).decode()
    print(json.dumps({"message" : message}))
except Exception as e:
    print("ERROR:{}".format(e))
