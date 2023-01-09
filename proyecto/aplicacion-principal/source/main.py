#!/usr/bin/env python3
from pyvis.network import Network
from ssh_connect import *
from module_scan import *
from enru import *
from dibujo import *
import re

arr = []
def crearG():
	# Listamos las interfaces de red aqui
	# interfaces=os.listdir("/sys/class/net/")
#	c=0
	# for i in range(len(interfaces)):
	#   print(f"{i+1}: {interfaces[i]}")
	# read=int(input("Ingresa el numero de interfaz: "))-1
	# Modulo que permite escanear todos los datos
	res = scan_by_interface("eth0","admin","admin01","12345678")

	general = res[0]
	interconexiones = res[1]
	routers = res[2]
	devices = res[3]
	global arr 
	arr = res[4]

	net = construirDibujoTopologia(routers, interconexiones, devices, general)
	net.save_graph("temp.html")
	cambiarEnlaces("temp.html", "templates/topo.html")
	eliminarTemporal("temp.html")

def crearU(router, user, pss, priv):
	
	cisco={
		"device_type":"cisco_xe",
		"ip":"",
		"username":"admin",
		"password":"admin01",
		"secret":"12345678"
	}
	cmd=["username "+user+" privilege "+priv+" password "+pss, "end", "wr"]
	
	try:
		if router == "Todos":
			for i in range(len(arr)):
				cisco["ip"] = arr[i]["ip"]
				if verificarU(cisco,user):
					print("El usuario "+user+" ya existe en "+arr[i]["hostname"])
				else:
					output=conectarT(cisco,cmd)
					print("Creación del usuario "+user+" exitosa en "+arr[i]["hostname"])
		else:
			for i in range(len(arr)):
				if arr[i]["hostname"] == router:
					cisco["ip"] = arr[i]["ip"]
					if verificarU(cisco,user):
						print("El usuario "+user+" ya existe en "+arr[i]["hostname"])
					else:
						output=conectarT(cisco,cmd)
						print("Creación del usuario "+user+" exitosa en "+arr[i]["hostname"])
	except:
		print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")

def modificarU(router, user, pss, priv):
	
	if verVacio(pss) or verVacio(priv):
		print("Debe llenar los campos faltantes...")
	else:
		cisco={
			"device_type":"cisco_xe",
			"ip":"",
			"username":"admin",
			"password":"admin01",
			"secret":"12345678"
		}
		cmd=["username "+user+" privilege "+priv+" password "+pss, "end", "wr"]

		try:
			if router == "Todos":
				for i in range(len(arr)):
					cisco["ip"] = arr[i]["ip"]
					if verificarU(cisco,user):
						output=conectarT(cisco,cmd)
						print("Modificación del usuario "+user+" exitosa en "+arr[i]["hostname"])
					else:
						print("No existe el usuario "+user+" a modificar en "+arr[i]["hostname"])						
			else:
				for i in range(len(arr)):
					if arr[i]["hostname"] == router:
						cisco["ip"] = arr[i]["ip"]
						if verificarU(cisco,user):
							output=conectarT(cisco,cmd)
							print("Modificación del usuario "+user+" exitosa en "+arr[i]["hostname"])
						else:
							print("No existe el usuario "+user+" a modificar en "+arr[i]["hostname"])
		except:
			print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")

def eliminarU(router, user):
	
	if user == "admin":
		print("No se puede eliminar al admin")
	else:
		cisco={
			"device_type":"cisco_xe",
			"ip":"",
			"username":"admin",
			"password":"admin01",
			"secret":"12345678"
		}
		cmd=["no username "+user, "end", "wr"]

		try:
			if router == "Todos":
				for i in range(len(arr)):
					cisco["ip"] = arr[i]["ip"]
					output=conectarT(cisco,cmd)
					print("Eliminación del usuario "+user+" exitosa en "+arr[i]["hostname"])
			else:
				for i in range(len(arr)):
					if arr[i]["hostname"] == router:
						cisco["ip"] = arr[i]["ip"]
						output=conectarT(cisco,cmd)
						print("Eliminación del usuario "+user+" exitosa en "+arr[i]["hostname"])
		except:
			print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")

def verificarU(cisco, user):
	cmd = ["sh running-config | i username"]

	usuarios = []
	output = conectar(cisco,cmd)
	m = re.split(r'\W+',output[0])
	for i in range(len(m)):
		if m[i] == "username":
			usuarios.append(m[i+1])
	for i in range(len(usuarios)):
		if usuarios[i] == user:
			return True
	return False

def obtHost():
	host = []
	try:
		for i in range(len(arr)):
			host.append(arr[i]["hostname"])
	except:
		print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")
	finally:
		return host

def obtInfoU():
	cisco={
		"device_type":"cisco_xe",
		"ip":"",
		"username":"admin",
		"password":"admin01",
		"secret":"12345678"
	}
	cmd = ["sh running-config | i username"]
#	arr=getRouters()
	
	try:
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
	except:
		print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")
#	return json_info

def enrutamiento(permiso, user, pasw, enr):
	global arr
	cisco={
		"device_type":"cisco_ios",
		"ip":"",
		"username":"admin",
		"password":"admin01",
		"secret":"12345678"
	}
	try:
		if enr == "RIP":
			if permiso == 0:
				cisco["username"] = user
				cisco["password"] = pasw

				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						init_rip_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
			else:
				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						print(arr[i]["ip"])
						init_rip_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
		elif enr == "OSPF":
			if permiso == 0:
				cisco["username"] = user
				cisco["password"] = pasw

				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						init_ospf_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
			else:
				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						print(arr[i]["ip"])
						init_ospf_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
		elif enr == "EIGRP":
			if permiso == 0:
				cisco["username"] = user
				cisco["password"] = pasw

				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						init_eigrp_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
			else:
				for i in range(len(arr)):
					if(arr[i]["hostname"]=="R1"):
						init_eigrp_ssh(arr[i]["ip"],cisco["username"],cisco["password"],cisco["secret"])
	except:
		print(" Arreglo de host no listo.\n Espere a que termine el escaneo...")

def verVacio(param):
	if param == "":
		return True
	else:
		return False

def getRouters():
	global arr
	rs = arr
	return rs