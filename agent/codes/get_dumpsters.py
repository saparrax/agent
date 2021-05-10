import sqlite3
import json


def load_dumpsters():
	conn = sqlite3.connect('/etc/agent/map.db')
	cursor = conn.cursor()
	data = cursor.execute('select * from dumpsters').fetchall()
	dumpsters = {}
	for dumpster in data:
		dumpsters[dumpster[0]] = dumpster[1]
	return dumpsters


if __name__ == "__main__":
    try:
        dumpsters = load_dumpsters()
        output = {
            'dumpsters': dumpsters,
        }
        print(json.dumps(output))
    except Exception as e:
        print("ERROR:{}".format(e))
