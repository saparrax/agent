"""First hug API (local and HTTP access)"""
""" find torna cursor, findOne torna dic"""
import hug
import pymongo
import json
import subprocess
import os
from bson import ObjectId
from pymongo import MongoClient




@hug.post('/execute')
def execute(body=None):
	print ('body' + str(body))
	output=subprocess.getoutput(body['python_version'] + " /etc/agent/codes/" + body['code'] + " " + body['params'])
	return {'response' : output}
	
@hug.get('/has_code')
def has_service_code(body=None):
	return os.path.isfile("/etc/agent/codes/" + body['code'])








