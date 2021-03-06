from multiprocessing import Process
import json, time, pickle
import sqlite3
import logging
import socket
import json
import ctypes
import commands
import requests
from threading import Thread
from subprocess import check_output



class DecisionMaker:

    STOP_DISTANCES = {
        0: 20,
        1: 10,
        2: 12,
        3: 13,
        4: 14,
        5: 15,
        6: 16,
        7: 17,
        8: 18,
        9: 19,
        10: 20
    }

    def __init__(self, car, params, rfid_queue, distance_queue, emergency=True):
        self.emergency = emergency
        self.car = car
	self.traffic_light_ip = params["GESTION_SEMAFOROS_ip"]
        self.traffic_light_port = int(params["GESTION_SEMAFOROS_port"])
	self.traffic_light_ips=self.traffic_light_ip.split(',')
	self.street_light_ip = params["GESTION_FAROLAS_ip"]
        self.street_light_port = int(params["GESTION_FAROLAS_port"])
	self.street_light_ips=self.street_light_ip.split(',')
        self.traffic_ip = params.get("GESTION_TRAFICO_ip")
        self.traffic_port = int(params.get("GESTION_TRAFICO_port"))
	self.rfid_queue = rfid_queue
        self.route_rfid = params["route_rfid"].split("@")
        self.route_rfid = self.route_rfid[:-1]
	print len(self.route_rfid)
	self.route_actions = json.loads(params["route_actions"])
        self.end = params["Final"]
        #self.end_request = self.route_rfid[-2] if len(self.route_rfid) >= 2 else None
        self.request_leader_info()
        self.set_first_rfid()
	self.last_rfid = self.load_last_rfid()
	print ("rfid inicial: " + str(self.last_rfid))
	self.s_traffic_light_sockets = []
	self.s_street_light_sockets = []
	self.ipsTrafficLights = []
	self.ipsStreetLights = []
	print "semafors: " + str(self.traffic_light_ips)
	print "fanals: " + str(self.street_light_ips)
	for i in range(len(self.traffic_light_ips)):
	    self.ip = self.traffic_light_ips[i]
	    print "socket semafors establert amb: " + str(self.ip) + ':' + str(self.traffic_light_port)
	    self.ipsTrafficLights.append(self.ip)
	    self.s_traffic_light = self.connect_socket(self.ip, self.traffic_light_port)
	    self.s_traffic_light_sockets.append(self.s_traffic_light)
	for i in range(len(self.street_light_ips)):
	    self.ip = self.street_light_ips[i]
	    print "socket fanals establert amb: " + str(self.ip) + ":" + str(self.street_light_port)
	    self.ipsStreetLights.append(self.ip)
	    self.s_street_light = self.connect_socket(self.ip, self.street_light_port)
	    self.s_street_light_sockets.append(self.s_street_light)
	print "socket transit establert amb: " + str(self.traffic_ip) + ':' + str(self.traffic_port)
	self.s_traffic = self.connect_socket(self.traffic_ip, self.traffic_port)
        self.distance = 9999
        self.last_emergency = 0
	self.ip = check_output(["hostname", "-I"]).strip()
 
    def set_first_rfid(self):
	setter = open("/etc/agent/config/car.config", "r+")
        content = json.load(setter)
        content["start_position"] = self.card_ids[self.route_rfid[0]]
        content["start_position_rfid"] = self.route_rfid[0]
	content["times"] = 0
	content["times_tl"] = 0
        setter.seek(0)
        json.dump(content, setter)
        setter.truncate()
        setter.close()

    def set_times_one(self):
        setter = open("/etc/agent/config/car.config", "r+")
        content = json.load(setter)
        content["times"] = 1
        setter.seek(0)
        json.dump(content, setter)
        setter.truncate()
        setter.close()

    def set_times_tl_one(self):
        setter = open("/etc/agent/config/car.config", "r+")
        content = json.load(setter)
        content["times_tl"] = 1
        setter.seek(0)
        json.dump(content, setter)
        setter.truncate()
        setter.close()

    def load_last_rfid(self):
        file = open("/etc/agent/config/car.config", "r")
        content = json.load(file)
        last_rfid = content["start_position_rfid"]
        file.close()
        return last_rfid

    def get_times(self):
        file = open("/etc/agent/config/car.config", "r")
        content = json.load(file)
        times = content["times"]
        file.close()
        return times

    def get_times_tl(self):
        file = open("/etc/agent/config/car.config", "r")
        content = json.load(file)
        times = content["times_tl"]
        file.close()
        return times


    def connect_socket(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((ip, port))
            return s
        except:
            time.sleep(1)
            return self.connect_socket(ip, port)


    def process_queue(self, rfid_queue, distance_queue):
        while True:
            if not rfid_queue.empty():
                info = rfid_queue.get()
                sel, value = info.split("-")
                if value in self.card_ids.keys():
                    self.last_rfid = value
                    self.reposition_car()
            if not distance_queue.empty():
                info = distance_queue.get()
                sel, value = info.split("-")
                self.distance = int(value)
            self.check_final()
	    if self.check_next_rfid() or self.emergency:
                if self.get_times_tl() == 0:
		    if self.check_traffic_lights():
                        self.check_distance()
                        self.check_route()
                    else:
                        self.car.brake()
		if self.get_times() == 0:
                #    print ('in')
		    self.check_streetlights()
            else:
                self.car.stop()


    def reposition_car(self):
        if self.last_rfid in self.card_ids.keys():
            if self.card_ids[self.last_rfid] != "P1":
		repeated = self.last_rfid == self.load_last_rfid()
                self.write_position_to_file(self.last_rfid, repeated)

    def write_position_to_file(self, rfid, rep):
        file = open("/etc/agent/config/car.config", "r+")
        content = json.load(file)
        content["start_position"] = self.card_ids[rfid]
        content["start_position_rfid"] = rfid
	if not rep:
	    print ("New rfid: " + self.card_ids[rfid])
	    content["times"]=0
	    content["times_tl"]=0
	else:
	    content["times"]=1
        file.seek(0)
        json.dump(content, file)
        file.truncate()
        file.close()

    def start(self, rfid_queue, distance_queue):
        self.process_queue_process = Process(target=self.process_queue, args=(rfid_queue, distance_queue,  ))
        self.process_queue_process.start()
        self.process_queue_process.join()

    def request_leader_info(self):
        # self.s_traffic_light.send("card_id_request".encode())
        # card_ids = self.s_traffic_light.recv(5096)
        # self.card_ids = json.loads(card_ids.decode())
        self.card_ids = self.load_card_ids()
        if self.emergency:
            # self.s_traffic_light.send("emergency_dict_request".encode())
            # emergency_trafficlights = self.s_traffic_light.recv(5096)
            # self.trafficlight_positions = json.loads(emergency_trafficlights.decode())
            self.trafficlight_positions = self.load_emergency_dict()
        else:
            # self.s_traffic_light.send("traffic_light_request".encode())
            # trafficlight_positions = self.s_traffic_light.recv(5096)
            # self.trafficlight_positions = json.loads(trafficlight_positions.decode())
            self.trafficlight_positions = self.load_traffic_lights()
	self.trafficlight_ips = self.load_traffic_lights_ip()
        # self.s_streetlight.send("streetlight_request".encode())
        # streetlight_positions = self.s_streetlight.recv(5096)
        # self.streetlight_positions = json.loads(streetlight_positions.decode())
        self.streetlight_positions = self.load_streetlights()
        self.streetlight_ips = self.load_streetlights_ip()

    # def message_received(self, rfid_queue):
    #     while True:
    #         message = self.s_traffic_light.recv(1024)
    #         if "responseTrafficLigtColor" in message:
    #             color = message.split('_')[1]
    #             rfid_queue.put("color-{}".format(color))

    def check_final(self):
	if self.last_rfid in self.card_ids.keys() and self.card_ids[self.last_rfid] == self.end:
	#if self.card_ids[self.last_rfid] == self.end:
	#avisar a transit que s'ha acabat la conduccio i alliberar posicio
	    if self.card_ids[self.last_rfid] == 'AB':
		print ('send end')
		msg = "setAgentPosition_{}_{}".format(self.ip, 'end')
                self.s_traffic.send(msg.encode())

	    print("Conduccion autonoma realizada correctamente")
            self.car.stop()
            exit(0)
	else:
	    return False
    
    def check_next_rfid(self):
        response = ''
        try:
            if self.check_traffic_lights_rfid() :
                index = self.route_rfid.index(self.last_rfid)
                tag = self.card_ids[self.route_rfid[index + 1]]
                msg = "setAgentPosition_{}_{}".format(self.ip, tag)
                self.s_traffic.send(msg.encode())
                response = self.s_traffic.recv(512).decode()
                if response == "free":
                    return True
                else:
                    return False
        except:
            return False

    def check_streetlights(self):
        if self.last_rfid in self.streetlight_positions.keys():
            streetlight = self.streetlight_positions[self.last_rfid]
	    ip = self.streetlight_ips[streetlight]
	    index = self.ipsStreetLights.index(ip)
	    self.s_street_light = self.s_street_light_sockets[index] 
            print ("Envia senyal per encendre " + streetlight)
	    self.s_street_light.send(("turnOnStreetlight_" + streetlight).encode())
	    self.set_times_one()

    def check_traffic_lights(self):
        if self.last_rfid in self.trafficlight_positions.keys():
            trafficlight = self.trafficlight_positions[self.last_rfid]
	    ip = self.trafficlight_ips[trafficlight]
	    index = self.ipsTrafficLights.index(ip)
	    #if trafficlight[-1:] == '1': trafficlight_pair=str(trafficlight[:2] + '2')
	    #elif trafficlight[-1:] == '2': trafficlight_pair=str(trafficlight[:2] + '1')
	    self.s_trafficlight = self.s_traffic_light_sockets[index]
            if not self.emergency:
                self.s_trafficlight.send(("requestTrafficLightStatus_" + trafficlight + "_circulacio").encode())
                traffic_light_status = self.s_trafficlight.recv(1024)
                traffic_light_status = traffic_light_status.split('_')[1]
		#self.s_traffic_light.send(("requestTrafficLightStatus_" + trafficlight_pair).encode())
                #traffic_light_status_pair = self.s_traffic_light.recv(1024)
                #traffic_light_status_pair = traffic_light_status_pair.split('_')[1]

                if traffic_light_status == "red" or traffic_light_status == "yellow":
                    self.car.brake()
                    return False
		#no faria falta si funciona be arduino
		#elif traffic_light_status == "green" and traffic_light_status_pair == "emergency":
		    #self.car.stop()
		    #return False
                elif self.car.is_car_stopped():
                    self.car.run()
		self.set_times_tl_one()
                return True

            elif self.last_emergency == 0:
                 self.last_emergency = 1
                 self.s_trafficlight.send(("setTrafficLightColor_{}_{}".format(trafficlight, "emergency")).encode())
                 return True
            else:
                 return True
        else:
            self.last_emergency = 0
            return True

    def check_traffic_lights_rfid(self):
	if self.get_times_tl() == 0 and self.last_rfid in self.trafficlight_positions.keys():
            trafficlight = self.trafficlight_positions[self.last_rfid]
            ip = self.trafficlight_ips[trafficlight]
            index = self.ipsTrafficLights.index(ip)
            #if trafficlight[-1:] == '1': trafficlight_pair=str(trafficlight[:2] + '2')
            #elif trafficlight[-1:] == '2': trafficlight_pair=str(trafficlight[:2] + '1')
            self.s_trafficlight = self.s_traffic_light_sockets[index]
            if not self.emergency:
                self.s_trafficlight.send(("requestTrafficLightStatus_" + trafficlight + "_test").encode())
                traffic_light_status = self.s_trafficlight.recv(1024)
                traffic_light_status = traffic_light_status.split('_')[1]
                #self.s_traffic_light.send(("requestTrafficLightStatus_" + trafficlight_pair).encode$
                #traffic_light_status_pair = self.s_traffic_light.recv(1024)
                #traffic_light_status_pair = traffic_light_status_pair.split('_')[1]

                if traffic_light_status == "red" or traffic_light_status == "yellow":
                    #self.car.brake()
                    return False
                #no faria falta si funciona be arduino
                #elif traffic_light_status == "green" and traffic_light_status_pair == "emergency":
                    #self.car.stop()
                    #return False
                else:
                    print 'stopped'
		    #self.car.run()
                return True

            elif self.last_emergency == 0:
                 self.last_emergency = 1
                 self.s_trafficlight.send(("setTrafficLightColor_{}_{}".format(trafficlight, "emergency")).encode())
                 return True
            else:
                 return True
        else:
            self.last_emergency = 0
            return True


    def check_distance(self):
        distance = self.distance
	#print 'distance: ' + str(distance) 
        if distance <= 10: 
	#self.STOP_DISTANCES[self.car.get_speed_level()]:
            self.car.brake()
        elif self.car.is_car_stopped() and self.last_rfid in self.card_ids.keys() and self.card_ids[self.last_rfid] != self.end:
            self.car.run()

    def check_route(self):
        if not self.car.is_car_stopped():
            if self.last_rfid in self.route_actions.keys():
                action = self.route_actions[self.last_rfid]
                if action == "turn_left":
                    self.car.left_corner()
                elif action == "turn_right":
                    self.car.right_corner()
                elif action == "go_straight":
                    self.car.go_straight()
                elif action == "stop":
                    self.car.stop()
            else:
                self.car.empty_action()
 
    def load_traffic_lights(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from traffic_lights").fetchall()
        trafficlights = {}
        for light in data:
            trafficlights[light[0]] = light[1]
        return trafficlights

    def load_traffic_lights_ip(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from traffic_lights_ip").fetchall()
        trafficlights_ip = {}
        for light in data:
            trafficlights_ip[light[0]] = light[1]
        return trafficlights_ip

    def load_emergency_dict(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from emergency_rfids").fetchall()
        emergency_dict = {}
        for emergency in data:
            emergency_dict[emergency[0]] = emergency[1]
        return emergency_dict

    def load_card_ids(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from card_id").fetchall()
        card_ids = {}
        for card_id in data:
            card_ids[card_id[1]] = card_id[0]
        return card_ids
    
    def load_streetlights(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from streetlights").fetchall()
        streetlights = {}
        for light in data:
            streetlights[light[0]] = light[1]
        return streetlights

    def load_streetlights_ip(self):
        conn = sqlite3.connect('/etc/agent/map.db')
        cursor = conn.cursor()
        data = cursor.execute("select * from streetlights_ip").fetchall()
        streetlights_ip = {}
        for light in data:
            streetlights_ip[light[0]] = light[1]
        return streetlights_ip
