import sqlite3
import socket
import requests
import sys
import os
import time
import json
from util import get_params


def main():
    urlFog = 'http://10.0.1.129:3001'
    portFog = '3001'
    urlCloud = 'http://147.83.159.200:3001'
    portCloud = '4321'
    trafficlight_positions = load_traffic_lights()
    trafficlight_ips = load_traffic_lights_ip()
    streetlight_positions = load_streetlights()
    streetlight_ips = load_streetlights_ip()
    mngmt = '10.0.1.88'
    params = get_params(sys.argv)
    list = params['llistaTag']
    #print list
    # [[llista], [llista]]
    list = list[1:-1]
    list = list.split('], [')
    #for i in range(len(list)):
	#print str(i) + str(list[i])
    #time.sleep(10)
    for i in range(len(list)):
	if i==0:
	    list[i] = list[i][1:]
	    #print str(i) + ' ' + str(list[i])
        elif i==len(list)-1:
	    list[i] = list[i][:-1]
	    #print str(i) + ' ' + str(list[i])
        #else:
	    #print str(i) + ' ' + str(list[i])
	sublist = list[i].split(', {')
	#print str(sublist)
	for ite in range(len(sublist)):
	    if ite!=0 :
	        sublist[ite] = '{' + sublist[ite] 
	    #print str(ite) + str(sublist[ite])
	#    list[i] = list[i][1:]
	#elif i==(len(list)-1):
	#    list[i] = '{' + list[i]
	#    list[i] = list[i][:-1]
	#else:
	#    list[i] = '{' + list[i] + '}'

        for x in range(len(sublist)):
            it = x
	    list_Ips=[]
	    end = sublist[x][-3:-1]
	    aux1 = sublist[x].split('{')
	    ra = aux1[2].split('}')[0]
	#tractar route actions
	    ract = ra.split(', ')
	    ractions = {}
	    for item in ract:
	        key, value=item.split(': ')
	        ractions[key] = value
	    ra = ractions
            aux2 = aux1[2].split('[')[1]
	#tractar route rfid
            rr = aux2.split(']')[0] 
	    rrf = rr.split(', ')
	    rrfid = ''
	    for y in range(len(rrf)):
	        rrfid = rrfid + str(rrf[y]) + '@'
	        if rrf[y] in trafficlight_positions.keys():
		    keyIp = trafficlight_positions[rrf[y]]
		    ip = trafficlight_ips[keyIp]
		    if ip not in list_Ips:
		        list_Ips.append(str(ip))
	        if rrf[y] in streetlight_positions.keys():
		    keyIp = streetlight_positions[rrf[y]]
		    ip = streetlight_ips[keyIp]
		    if ip not in list_Ips:
		        list_Ips.append(str(ip))


	    data = {}
	    data['Final'] = end
	    data['route_actions'] = ra
	    data['route_rfid'] = rrfid
	    json_data = json.dumps(data)

	    json_object = json.loads(json_data)
	    result = ""
	    for key, value in json_object.items():
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
	    if mngmt not in list_Ips:
	        list_Ips.append(mngmt)

	    print "ips involucrades: " + str(list_Ips)
	    ips = ''
	    for item in range(len(list_Ips)):
	        ips = ips + str(list_Ips[item]) + ','
	    ips = ips[:-1] 
	    result = result + "GESTION_SEMAFOROS_ip=" + ips + " GESTION_SEMAFOROS_port=5000 " 
	    result = result + "GESTION_FAROLAS_ip=" + ips + " GESTION_FAROLAS_port=5002 " 
	    result = result + "GESTION_TRAFICO_ip=" + ips +  " GESTION_TRAFICO_port=5004 " 
	    #result = result + "GESTION_SEMAFOROS_ip=192.168.1.112 GESTION_SEMAFOROS_port=5000 " 
	    #result = result + "GESTION_FAROLAS_ip=192.168.1.112 GESTION_FAROLAS_port=5002 " 
	    print ('python follow_route_fisico.py ' + result)
	    os.system('python /etc/agent/codes/follow_route_fisico.py ' + result)
            idRecollida = params['id']
	    if it==len(sublist)-1:
	        jsondata = {}
                #hostname = socket.gethostname()
                #ipVehicle = socket.gethostbyname(hostname)
                jsondata['idServei'] = idRecollida
                jsondata['servei'] = 'RECOLLIDA'
	        print ("request.abocador")
                requests.post(urlCloud + '/abocador', json=jsondata)
	    else:
	        jsondata = {}
                jsondata['idRecollida'] = idRecollida
                jsondata['idUbicacio'] = end
                print ("request.carregaRecollida a " + end)
                requests.post(urlCloud + '/carregaRecollida', json=jsondata)
	    time.sleep(5)
    	#print 'end iter'


	#print ('python follow_route_fisico.py ' + json.dumps(list[i]))
	#time.sleep(5)
    #os.system('python stop.py')

def load_traffic_lights():
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from traffic_lights").fetchall()
        trafficlights = {}
        for light in data:
            trafficlights[light[0]] = light[1]
        return trafficlights

def load_traffic_lights_ip():
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        print 'hola'
	data = cursor.execute("select * from traffic_lights_ip").fetchall()
        trafficlights_ip = {}
        for light in data:
            trafficlights_ip[light[0]] = light[1]
        return trafficlights_ip

def load_streetlights():
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from streetlights").fetchall()
        streetlights = {}
        for light in data:
            streetlights[light[0]] = light[1]
        return streetlights

def load_streetlights_ip():
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from streetlights_ip").fetchall()
        streetlights_ip = {}
        for light in data:
            streetlights_ip[light[0]] = light[1]
        return streetlights_ip


if __name__ == "__main__":
    main()


