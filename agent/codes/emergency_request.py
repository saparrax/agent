<<<<<<< HEAD
import json
import requests
import sys
from util import get_params


def get_nearest_ambulance():
     if node_info["role"] == "cloud_agent":
         ambulances = get_all_ambulances()
         if len(ambulances) > 0:
             ambulance = ambulances[0]
             service = {
                 "service_id": "EMERGENCY_SERVICE",
                 "agent_ip": ambulance["myIP"],
                 "params": {
                     "agent_id": ambulance["nodeID"],
                     "Final": params["Final"]
                 }
             }
             if ambulance["role"] == "agent":
                 print(requests.post("http://{}:8000/request_service".format(ambulance["leaderIP"]), json=service).text)
             else:
                 print(requests.post("http://{}:8000/request_service".format(ambulance["myIP"]), json=service).text)
         else:
             print("No hay ambulancias disponibles en este momento")
     elif node_info["role"] == "leader":
         ambulances = get_my_ambulances()
         if len(ambulances) > 0:
             ambulance = ambulances[0]
             service = {
                 "service_id": "EMERGENCY_SERVICE",
                 "agent_ip": ambulance["myIP"],
                 "params": {
                     "agent_id": ambulance["nodeID"],
                     "Final": params["Final"]
                 }
             }
             print(requests.post("http://{}:8000/request_service".format(node_info["myIP"]), json=service).text)
        else:
            service = {
                "service_id": "SEARCH_NEAREST_AMBULANCE",
                "params": {
                    "Final": params["Final"]
                }
            }
            print(requests.post("http://{}:8000/execute_service".format(node_info["leaderIP"]), json=service).text)

def get_my_ambulances():
    request_info = json.dumps({"leaderIP": node_info["myIP"], "device": "ambulance", "status": 1})
    ambulances = requests.get("http://{}:8000/agent/{}".format(node_info["myIP"], request_info)).json()
    return ambulances

def get_all_ambulances():
    request_info = json.dumps({"device": "ambulance", "status": 1})
    ambulances = requests.get("http://{}:8000/agent/{}".format(node_info["myIP"], request_info)).json()
    return ambulances

if __name__ == '__main__':
    try:
        params = get_params(sys.argv)
        node_info = json.load("/etc/agent/config/device.config")
        get_nearest_ambulance()
    except Exception as e:
        print("ERROR:{}".format(e))
=======
import json
import requests
import sys
from util import get_params


def get_nearest_ambulance():
     if node_info["role"] == "cloud_agent":
         ambulances = get_all_ambulances()
         if len(ambulances) > 0:
             ambulance = ambulances[0]
             service = {
                 "service_id": "EMERGENCY_SERVICE",
                 "agent_ip": ambulance["myIP"],
                 "params": {
                     "agent_id": ambulance["nodeID"],
                     "Final": params["Final"]
                 }
             }
             if ambulance["role"] == "agent":
                 print(requests.post("http://{}:8000/request_service".format(ambulance["leaderIP"]), json=service).text)
             else:
                 print(requests.post("http://{}:8000/request_service".format(ambulance["myIP"]), json=service).text)
         else:
             print("No hay ambulancias disponibles en este momento")
     elif node_info["role"] == "leader":
         ambulances = get_my_ambulances()
         if len(ambulances) > 0:
             ambulance = ambulances[0]
             service = {
                 "service_id": "EMERGENCY_SERVICE",
                 "agent_ip": ambulance["myIP"],
                 "params": {
                     "agent_id": ambulance["nodeID"],
                     "Final": params["Final"]
                 }
             }
             print(requests.post("http://{}:8000/request_service".format(node_info["myIP"]), json=service).text)
        else:
            service = {
                "service_id": "EMERGENCY_REQUEST",
                "params": {
                    "Final": params["Final"]
                }
            }
            print(requests.post("http://{}:8000/execute_service".format(node_info["leaderIP"]), json=service).text)
    else:
        service = {
            "service_id": "EMERGENCY_REQUEST",
            "params": {
                "Final": params["Final"]
            }
        }
        print(requests.post("http://{}:8000/execute_service".format(node_info["leaderIP"]), json=service).text)    

def get_my_ambulances():
    request_info = json.dumps({"leaderIP": node_info["myIP"], "device": "ambulance", "status": 1})
    ambulances = requests.get("http://{}:8000/agent/{}".format(node_info["myIP"], request_info)).json()
    return ambulances

def get_all_ambulances():
    request_info = json.dumps({"device": "ambulance", "status": 1})
    ambulances = requests.get("http://{}:8000/agent/{}".format(node_info["myIP"], request_info)).json()
    return ambulances

if __name__ == '__main__':
    try:
        params = get_params(sys.argv)
        node_info = json.load("/etc/agent/config/device.config")
        get_nearest_ambulance()
    except Exception as e:
        print("ERROR:{}".format(e))
>>>>>>> e8df961f35fc2cec11beeb5c91af79be3693666d
