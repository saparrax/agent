import sys
import json
import socket
import sqlite3
import errno
from threading import Thread
from util import get_params
# from frontend_connection import FrontendConnection


CARD_ID_REQUEST = "card_id_request"
SET_AGENT_POSITION = "setAgentPosition"

def load_card_ids():
    conn = sqlite3.connect('/etc/agent/map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from card_id").fetchall()
    card_ids = {}
    for card_id in data:
        card_ids[card_id[1]] = card_id[0]
    return card_ids


def bind_connection():
        my_socket.bind((ip, port))
        my_socket.listen(50)

def accept_connection():
        while True:
            agent_connection, addr = my_socket.accept()
            print("Se ha conectado el agent con addr ", addr)
            agent_connection.setblocking(0)
            agents.append(agent_connection)

def update_rfid_status(data):
    car_id = data[1]
    next_position = data[2]

    if cars_position.get(car_id) == next_position:
        return "free"
    elif rfid_status[next_position] == 0:
        previous_position = cars_position.get(car_id)
        if previous_position:
            rfid_status[previous_position] = 0
        rfid_status[next_position] = 1
        cars_position[car_id] = next_position
        return "free"
    else:
        return "busy"



def receive_request():
    while True:
        for agent in agents:
            try:
                msg = agent.recv(4096).decode()
                if msg != None and msg != "":
                    print(msg)
                    info = ""
                    if msg == CARD_ID_REQUEST:
                        info = json.dumps(card_id_dict, ensure_ascii=False)
                    elif msg.split("_")[0] == SET_AGENT_POSITION:
                        data = msg.split("_")
                        info = update_rfid_status(data)
                    if info != "":
                        print(info)
                        agent.send(info.encode())
            except IOError as e:
                if(e.errno == errno.EWOULDBLOCK):
                    pass


def create_rfid_status():
    rfid_status = {}
    for tag, position in card_id_dict.items():
        rfid_status[position] = 0
    return rfid_status

if __name__ == "__main__":
    params = get_params(sys.argv)
    download_host = params.get("download_host")
    download_port = params.get("download_port")
    ip = params.get("ip")
    port = int(params.get("port"))
    # load from db
    card_id_dict = load_card_ids()
    rfid_status = create_rfid_status()
    cars_position = {}
    agents = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bind_connection()
    Thread(target=accept_connection).start()
    # Thread(target=receive_request).start()
    receive_request()

    # frontend = FrontendConnection(download_host, download_port) # Conexion con Frontend
