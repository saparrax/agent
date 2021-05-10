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
    # [['N5', 'C3'], ['S7'], ['B5']]
    # posicions first, mid, last
    ab = params['abocador']
    l = l[1:-1]
    # ['N5', 'C3'], ['S7'], ['B5']
    list_routes = l.split('], ')
    # ['N5', 'C3'
    # ['S7'
    # ['B5']
    llistaTotal = []
    routeParcial = []

    for i in range(len(list_routes)):
        position = ''
	it = i
        if i == 0:
            position = 'start'
	    l1 = list_routes[i][1:]
	    # str(list_routes[i]).append(']')
        elif i == (len(list_routes)-1):
            position = 'end'
	    l1 = list_routes[i][1:-1]
        else:
            position = 'mid'
	    l1 = list_routes[i][1:]
	    # str(list_routes[i]).append(']')
        posInicial = 'AB'
        posInter = 'E4'
        posFinal = 'AB'
        l = l1.split(', ')
        list = l
        best_comb = ''
        w_best_comb = 0
        w_route_actions = ''
        end = False
        card_ids = load_card_ids()

        for i in itertools.permutations(list):
	    j = len(i)
	    y = 0
            end = False
            w = 0
            ra = ''
            while not end:
                while y <= j:
                    if y == 0:
                        if position == 'start':
                            cmd = "python /etc/agent/codes/shortest_route.py Inicio=AB Final=" + \
                                i[y]
#			    print cmd
                        else:
                            cmd = "python /etc/agent/codes/shortest_route.py Inicio=E4 Final=" + \
                                i[y]
#			    print cmd
                    elif y == j:
                        if position == 'end':
                    	    cmd = "python /etc/agent/codes/shortest_route.py Inicio=" + \
                    	        i[y-1] + " Final=AB"
#			    print cmd
                    	else:
                            cmd = "python /etc/agent/codes/shortest_route.py Inicio=" + \
                                i[y-1] + " Final=E4"
#		   	    print cmd
                    else:
                        cmd = "python /etc/agent/codes/shortest_route.py Inicio=" + \
                            i[y-1] + " Final="+i[y]
#			print cmd
            	    y = y+1
		result = subprocess.check_output(cmd, shell=True)
		resp = json.loads(result)
                w = w + len(resp['route_rfid'])
                # print ('comb ' +str(i)  + " with weight " + str(w))
                if w_best_comb == 0 or w < w_best_comb:
                    w_best_comb = w
                    best_comb = i
                for item in range(len(best_comb)):
                    list[item] = best_comb[item]
                end = True
	if position == 'start':
	    list.append(posInter)
            list.insert(0, posInicial)
        if position == 'mid':
	    list.append(posInter)
            list.insert(0, posInter)
        if position == 'end':
	    list.append(posFinal)
            list.insert(0, posInter)

        json_response = '{"ruta_final": "' + str(list) + '"}'
        json_rfid = {}
        for item in range(len(list)-1):
            cmd = "python /etc/agent/codes/shortest_route.py Inicio=" + \
                list[item] + " Final="+list[item+1]
	    result = subprocess.check_output(cmd, shell=True)
	    resp = json.loads(result)
            ra = resp['route_actions']
            rrfid = resp['route_rfid']
            id = str(list[item] + list[item+1])
            new_json = {id: ra}
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

            rfid = route_rrfid[str(list[item] + list[item+1])]

            output = {
                'Final': str(list[item+1]),
                'route_actions': ra,
                'route_rfid': rfid,
            }
            route.append(output)
	    
            
	routeParcial.append(route)
    data = {}
    data['llistaTag'] = routeParcial
    print json.dumps(data)

    
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
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
