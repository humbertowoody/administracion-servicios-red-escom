from pyvis.network import Network
from ssh_connect import *
from main import *
import re

crearG()

cisco={
	"device_type":"cisco_xe",
	"ip":"",
	"username":"admin",
	"password":"admin01",
	"secret":"12345678"
}
cmd = ["sh running-config | i username"]
arr=getRouters()

info = []
for i in range(len(arr)):
	hname = arr[i]["hostname"]
	info_n = {"hostname":hname, "usuarios":[]}
	cisco["ip"] = arr[i]["ip"]
	output = conectar(cisco,cmd)
	m = re.split(r'\W+',output[0])
	inter=[]
	for i in range(len(m)):
		if (i==0) or (i/7==1):
			a = {"usuario":m[i+1],
				 "privilegio":m[i+3],
				 "contrasenia":m[i+6]}
			inter.append(a)
	info_n["usuarios"] = inter
	info.append(info_n)
json_info=json.dumps(info,sort_keys=True,indent=4)
print(f"Información:\n{json_info}")