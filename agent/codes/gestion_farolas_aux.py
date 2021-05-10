import time
import sys
import json
import socket
import sqlite3
import errno
import serial
from threading import Thread
from util import get_params
from frontend_connection import FrontendConnection


STREETLIGHT_REQUEST = "streetlight_request"
TURN_ON_STREETLIGHT = "turnOnStreetlight"
CALIBRATE_STREET_LIGHT = "calibrate_street_light"


# Propiedades y caracteristicas de los agentes que representa este script
f1 = {
    "id" : "F1",
    "type" : "streetlight",
    "positioning" : "rfid",
    "x" : 315,
    "y" : 818,
    "status" : 0,
    "description" : "Farola",
    "attributtes" : {
        "role" : "agent",
        "leader" : "F4",
        "resources" : {
            "CPU" : "1GHz",
            "Chipset" : "DDR4",
            "DISK" : 50
        },
        "iots" : {}
    }
}

f2 = {
    "id" : "F2",
    "type" : "streetlight",
    "positioning" : "rfid",
    "x" : 433,
    "y" : 818,
    "status" : 0,
    "description" : "Farola",
    "attributtes" : {
        "role" : "agent",
        "leader" : "F4",
        "resources" : {
            "CPU" : "1GHz",
            "Chipset" : "DDR4",
            "DISK" : 50
        },
        "iots" : {}
    }
}

f3 = {
    "id" : "F3",
    "type" : "streetlight",
    "positioning" : "rfid",
    "x" : 664,
    "y" : 818,
    "role" : "agent",
    "leader" : "F4",
    "status" : 0,
    "description" : "Farola",
    "attributtes" : {
        "role" : "agent",
        "leader" : "F4",
        "resources" : {
            "CPU" : "1GHz",
            "Chipset" : "DDR4",
            "DISK" : 50
        },
        "iots" : {}
    }
}

f4 = {
    "id" : "F4",
    "type" : "streetlight",
    "positioning" : "rfid",
    "x" : 905,
    "y" : 818,
    "status" : 0,
    "description" : "Farola",
    "attributtes" : {
        "role" : "leader",
        "leader" : "",
        "resources" : {
            "CPU" : "1GHz",
            "Chipset" : "DDR4",
            "DISK" : 50
        },
        "iots" : {}
    }
}

f5 = {
    "id" : "F5",
    "type" : "streetlight",
    "positioning" : "rfid",
    "x" : 1023,
    "y" : 818,
    "status" : 0,
    "description" : "Farola",
    "attributtes" : {
        "role" : "agent",
        "leader" : "F4",
        "resources" : {
            "CPU" : "1GHz",
            "Chipset" : "DDR4",
            "DISK" : 50
        },
        "iots" : {}
    }
}


def bind_connection():
        my_socket.bind((ip, port))
        my_socket.listen(50)

def accept_connection():
        while True:
            agent_connection, addr = my_socket.accept()
            print("Se ha conectado el agent con addr ", addr)
            agent_connection.setblocking(0)
            agents.append(agent_connection)

def calibrate_street_light():
    try:
        streetlight_arduino.write("calibration".encode())
        return "Street lights calibrated successfully"
    except Exception as e:
        return "ERROR:{}".format(e)

def receive_request():
    while True:
        for agent in agents:
            try:
                msg = agent.recv(4096).decode()
                if(msg != None and msg != ""):
                    print(msg)
                    info = ""
                    if msg == STREETLIGHT_REQUEST:
                        info = json.dumps(streetlight_dict, ensure_ascii=False)
                    elif msg == CALIBRATE_STREET_LIGHT:
                        info = calibrate_street_light()
                    elif msg.split('_')[0] == TURN_ON_STREETLIGHT:
                        light_id = msg.split('_')[1]
                        data = {
                            'light_id': light_id,
                        }
                        on_receive_status(data)
                    if info != "":
                        print(info)
                        agent.send(info.encode())
            except IOError as e:
                if(e.errno == errno.EWOULDBLOCK):
                    pass


def load_streetlights():
    conn = sqlite3.connect('/etc/agent/map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from streetlights").fetchall()
    streetlights = {}
    for light in data:
        streetlights[light[0]] = light[1]
    return streetlights



def on_receive_status(*args):
    print(args)
    data = args[0]
    if data.get("agente_id") and data.get("status"):
        arduino_message = data["agente_id"]+"_"+data["status"]
        streetlight_arduino.write(arduino_message.encode())
        frontend.sendStatus(data["agente_id"], data["status"])
    elif data.get("light_id"):
        light_id = data.get("light_id")
        streetlight_arduino.write(light_id.encode())
        if light_id == "1":
            frontend.sendStatus("F1", "1")
        if light_id == "2":
            frontend.sendStatus("F1", "2")
            frontend.sendStatus("F2", "1")
        if light_id == "3":
            frontend.sendStatus("F1", "1")
            frontend.sendStatus("F2", "2")
            frontend.sendStatus("F3", "1")
        if light_id == "4":
            frontend.sendStatus("F2", "1")
            frontend.sendStatus("F3", "2")
        if light_id == "5":
            frontend.sendStatus("F2", "1")
            frontend.sendStatus("F3", "2")
            frontend.sendStatus("F4", "1")
        if light_id == "6":
            frontend.sendStatus("F3", "2")
            frontend.sendStatus("F4", "1")
        if light_id == "7":
            frontend.sendStatus("F3", "1")
            frontend.sendStatus("F4", "2")
            frontend.sendStatus("F5", "1")
        if light_id == "8":
            frontend.sendStatus("F4", "1")
            frontend.sendStatus("F5", "2")
        if light_id == "9":
            frontend.sendStatus("F5", "1")

def receive_frontend_request():
    if frontend:
       frontend.socket.on("front/agent/status", on_receive_status)
    while True:
        frontend.wait(1)

if __name__ == "__main__":
    try:
        params = get_params(sys.argv)
        download_host = params.get("download_host")
        download_port = params.get("download_port")
        ip = params.get("ip")
        port = int(params.get("port"))
        # load from db
        streetlight_dict = load_streetlights()

        agents = []
        streetlight_arduino = serial.Serial('/dev/arduinos/fs', 9600)
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_connection()
        Thread(target=accept_connection).start()
        Thread(target=receive_request).start()
        frontend = FrontendConnection(download_host, download_port) # Conexion con Frontend
        if frontend:
            Thread(target=receive_frontend_request).start()
        frontend.recognizeAgent(f1)
        frontend.recognizeAgent(f2)
        frontend.recognizeAgent(f3)
        frontend.recognizeAgent(f4)
        frontend.recognizeAgent(f5)

    except Exception as e:
        print("ERROR:{}".format(e))
