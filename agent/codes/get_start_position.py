import json

try:
    p_file = open("/etc/agent/config/car.config", "r")
    content = json.load(p_file)
    position = content["start_position"]
    p_file.close()
    print(json.dumps({"Inicio": position}))
except Exception as e:
    try:
        position = {"start_position": "NW", "start_position_rfid": "41 205 254 41"}
        p_file = open("/etc/agent/config/car.config", "w")
        json.dump(position, p_file)
        p_file.close()
        print(json.dumps({"Inicio": position}))
    except Exception as ne:
        print("Error:{}".format(ne))
