import itertools
import subprocess
import json
import sys
import ast
import sqlite3
from util import get_params

def main():
    params = get_params(sys.argv)
    l = params['llistaTag']
    ab = params['abocador']
    l = l[1:-1]
    l = l.split(', ')
    list = l
    best_comb = ''
    w_best_comb = 0
    w_route_actions = ''
    end = False
    card_ids = load_card_ids()

    for i in itertools.permutations(list):
        j = len(i)
        y=0
        end = False
        w = 0
        ra = ''
        while not end:
	    while y<=j:
	        if y==0:
		    cmd="python /etc/agent/codes/shortest_route.py Inicio=AB Final="+i[y]
	        elif y==j:
	            cmd = "python /etc/agent/codes/shortest_route.py Inicio="+i[y-1] + " Final=AB"
	        else:
	            cmd = "python /etc/agent/codes/shortest_route.py Inicio="+i[y-1] + " Final="+i[y]
		y=y+1
	        result = subprocess.check_output(cmd, shell=True)
	        resp = json.loads(result)
	        w = w + len(resp['route_rfid'])
            #print ('comb ' +str(i)  + " with weight " + str(w))
	    if w_best_comb==0 or w<w_best_comb:
	        w_best_comb = w
	        best_comb = i
	    for item in range(len(best_comb)):
	        list[item] = best_comb[item]
	    end = True
    list.append(ab)
    list.insert(0, ab)
    #print str(list)
    #print ('best comb ' + str(best_comb) + " with weight " + str(w_best_comb))
    json_response = '{"ruta_final": "' + str(list) + '"}'
    json_rfid = {}
    for item in range(len(list)-1):
        cmd = "python /etc/agent/codes/shortest_route.py Inicio="+list[item] + " Final="+list[item+1]
        result = subprocess.check_output(cmd, shell=True)
        resp = json.loads(result)
        ra = resp['route_actions']
	rrfid = resp['route_rfid']
        id = str(list[item] + list[item+1]) 
        new_json = {id : ra}
	json_rfid[id] = rrfid	
	aux = json.loads(json_response)
        aux.update(new_json)
        json_response = json.dumps(aux)
    route_rfid = json.dumps(json_rfid)
    
    route = []
    for item in range(len(list)-1):
        route_actions = json_loads_byteified(json_response)
        route_rrfid = json_loads_byteified(route_rfid)
	ra = route_actions[str(list[item] + list[item+1])]
	#for pos, tag in card_ids.items():
    	#    if tag == str(list[item]):
        #        rfid  = pos
        rfid = route_rrfid[str(list[item] + list[item+1])]
	#rAct = [s.encode('utf-8')  for s in ra]
	#ract = json.dumps(ra)
	#r = "Final=" + str(list[item+1]) + " route_actions=" + ract + " route_rfid=" + rfid + '@'
	#route.append(r)
	output = {
            'Final': str(list[item+1]),
	    'route_actions': ra,
            'route_rfid': rfid,
	}
	route.append(output)

    data = {}
    data['llistaTag']= route
    print json.dumps(data)
#list = []
    #for i in range(len(route)):
	#print routes[i]
	#list.append(route[i])
	#if i==len(routes)-1:
	    #print ("API call a Descarrega / Final execucio")
	#else:
	    #print ("API call a Carrega")
    #print list
    #print list[0]
    #print list[1]
    #print list[2]


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
