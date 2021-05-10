import itertools
import subprocess
import json
import sys
import ast
import sqlite3
from util import get_params

def main():
    #inici = sys.argv[1]
    #desti = ''
    #if len(sys.argv) == 3:
        #ab = sys.argv[2]
    #elif len(sys.argv) == 4:
	#desti = sys.argv[2]
	#ab = sys.argv[3]
    params = get_params(sys.argv)
    r = params['llistaTag']
    r = r[1:-1]
    r = r.split(', ')
    inici = r[0]
    desti = ''
    if len(r) == 2:
        desti=r[1]

    ab = params['abocador']

    card_ids = load_card_ids()
    route = []
    route.append(ab)
    route.append(inici)
    if desti != '' : route.append(desti)
    route.append(ab)

    json_response = '{"ruta_final": "' + str(list) + '"}'    
    json_rfid = {}
    for item in range(len(route)-1):
        cmd = "python /etc/agent/codes/shortest_route.py Inicio="+route[item] + " Final="+route[item+1]
        result = subprocess.check_output(cmd, shell=True)
        resp = json.loads(result)
        ra = resp['route_actions']
        rrfid = resp['route_rfid']
	id = str(route[item] + route[item+1]) 
        new_json = {id : ra}
	json_rfid[id] = rrfid
        aux = json.loads(json_response)
        aux.update(new_json)
        json_response = json.dumps(aux)
    route_rfid = json.dumps(json_rfid)

    routeReserva = []
    for item in range(len(route)-1):
        route_actions = json_loads_byteified(json_response)
	route_rrfid = json_loads_byteified(route_rfid)
        ra = route_actions[str(route[item] + route[item+1])]
	#for pos, tag in card_ids.items():
    	#    if tag == str(route[item]):
        #        rfid  = pos
	rfid = route_rrfid[str(route[item] + route[item+1])]
        #rAct = [s.encode('utf-8')  for s in ra]
	#ract = json.dumps(ra)
        #r = "Final=" + str(route[item+1]) + " route_actions=" + ract + " route_rfid=" + rfid + '@' 
	#routeReserva.append(r)

        output = {
	    'Final': str(route[item+1]),
	    'route_actions': ra,
	    'route_rfid': rfid,
	}
	routeReserva.append(output)
    
    data = {}
    data['llistaTag'] = routeReserva
    print json.dumps(data)
	#print routes[i]
	#if i==0:
	#    print ("API call a Carrega")
	#elif i==1 and len(routes)==3:
	#    print ("API call a Descarrega")
	#elif i==len(routes)-1 and len(routes)==2:
	#    print ("API call a Descarrega / Execucio final")
	#elif i==len(routes)-1 and len(routes)==3:
	#    print ("Execucio final")

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data




def deunicodify_hook(pairs):
    new_pairs = []
    for key, value in pairs:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        new_pairs.append((key, value))
    return dict(new_pairs)


def load_card_ids():
    conn = sqlite3.connect('/etc/agent/map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from card_id").fetchall()
    card_ids = {}
    for card_id in data:
        card_ids[card_id[1]] = card_id[0]
    return card_ids

if __name__ == "__main__":
    main()
