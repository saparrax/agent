import sys
import subprocess
import requests
import json
from util import get_params

def prepare_params(params):
    result = ""
    if params:
        for key, value in params.items():
            if value:
                if(type(value) is dict):
                    result += key + "='" + json.dumps(value) + "' "
                elif(type(value) is list):
                    result += key + "="
                    for item in value:
                        result+=item+"@"
                    result += " "
                elif value != "":
                    result += key + "=" + str(value) + " "
    return result

def get_route(my_ip, agent_id, params):
    response = requests.post(
        "http://{}:8000/request_service".format(my_ip),
        json={"service_id": "SHORTEST_ROUTE", "agent_id": agent_id, "params": params}
    )
    route = json.loads(json.loads(response.text).get("output"))
    for key, value in params.items():
        if key not in route.keys():
            route[key] = params[key]
    return route


params = get_params(sys.argv)
my_ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
agent_id = params["agent_id"]
dumpsters = json.loads(params["dumpsters"])

while True:
    for dumpster in dumpsters.keys():
        params["Final"] = dumpster
        route = get_route(my_ip, agent_id, params)
        route = prepare_params(route)
        output = subprocess.getoutput("python2 /etc/agent/codes/follow_route_fisico.py " + route)
        params["Inicio"] = params["Final"]
