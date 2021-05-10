import sqlite3
import time
import json
import sys
import random
from util import get_params


def load_rfid_intersections():
	conn = sqlite3.connect('/etc/agent/map.db')
	cursor = conn.cursor()
	data = cursor.execute('select * from rfid_intersections').fetchall()
	rfid_intersections = {}
	for rfid_intersection in data:
		rfid_intersections[rfid_intersection[0]] = rfid_intersection[1]
	return rfid_intersections

def load_card_id():
	conn = sqlite3.connect('/etc/agent/map.db')
	cursor = conn.cursor()
	data = cursor.execute('select * from card_id').fetchall()
	card_ids = {}
	for card_id in data:
		card_ids[card_id[0]] = card_id[1]
	return card_ids

def load_rfid_connections():
	conn = sqlite3.connect('/etc/agent/map.db')
	cursor = conn.cursor()
	connections = cursor.execute('select * from rfid_connections').fetchall()
	rfid_connections = {}
	for rfid_connection in connections:
		rfid_connections[rfid_connection[0]] = rfid_connection[1].split(',')
	return rfid_connections

def load_rfid_turns():
	conn = sqlite3.connect('/etc/agent/map.db')
	cursor = conn.cursor()
	turns = cursor.execute('select * from rfid_turns').fetchall()
	rfid_turns = {}
	for rfid_turn in turns:
		rfid_turns[rfid_turn[0]] = rfid_turn[1]
	return rfid_turns

def get_shortest_route(start, end):
	if start in rfid_connections:
		route = shortest_path(rfid_connections, start, end)
		return car_route(route, end)
	else:
		return None, None

def car_route(route, end):
	route_actions = {}
	rfid_route = []
	for i in range(len(route)):
		rfid_route.append(card_id[route[i]])
		if(i+1 < len(route)):
			section = route[i] + route[i+1]
			if section in rfid_turns:
				route_actions[card_id[route[i]]] = rfid_turns[section]
				if route[i] in rfid_intersections:
					rfid_route.append(card_id[rfid_intersections[route[i]]])
	route_actions[card_id[end]] = "stop"
	return route_actions, rfid_route

def shortest_path(graph, start, end, path=[]):
	if start in path:
		return None
	path = path + [start]
	if start == end:
		return path
	if not start in graph.keys():
		return None
	shortest = None
	for node in graph[start]:
		if node not in path:
			new_path = shortest_path(graph, node, end, path)
			if new_path:
				if not shortest or len(new_path) < len(shortest):
					shortest = new_path
	return shortest


if __name__ == "__main__":
        try:
                rfid_connections = load_rfid_connections()
                rfid_turns = load_rfid_turns()
                card_id = load_card_id()
                rfid_intersections  = load_rfid_intersections()

                params = get_params(sys.argv)
                if not params.get("Inicio"):
                        params["Inicio"] = random.choice(list(rfid_connections.keys()))
                if not params.get("Final"):
                        params["Final"] = random.choice(list(rfid_connections.keys()))
                route_actions, route_rfid = get_shortest_route(params["Inicio"], params["Final"])

                output = {
                        'route_actions': route_actions,
                        'route_rfid': route_rfid,
						'Final': params["Final"]
                }
                print(json.dumps(output))
        except Exception as e:
                print("ERROR:{}".format(e))
