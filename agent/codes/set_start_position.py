import json
import sys
from util import get_params


try:
  params = get_params(sys.argv)
  p_file = open("/etc/agent/car.config", "w") 
  json.dump({"start": params["Inicio"]}, p_file)
  p_file.close()
  print(json.dumps{"Inicio": params["Inicio"]})
except Exception, e:
  print("ERROR:{}".format(e))
