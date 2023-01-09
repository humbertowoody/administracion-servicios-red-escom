from netmiko import ConnectHandler
import netifaces as ni
from detecta import *
import os

user = 'admin'
password = 'admin01'
secret = '12345678'
host = 'R1'
sb=1
sbb=0

#esto es para conectarnos mediante SSH
cisco = {
	"device_type":"cisco_ios",
	'ip': "",
    "username":"",
    "password":"",
    "secret":"12345678"
}

#esto es para conectarnos mediante telnet
ciscot = {
	"device_type":"cisco_ios_telnet",
	'ip': "",
    "username":"",
    "password":"",
    "secret":"1234"
}


known_routers = []

# Listamos las interfaces de red aqui
interfaces=os.listdir("/sys/class/net/")
c=0
for i in range(len(interfaces)):
    print(f"{i+1}: {interfaces[i]}")
read=int(input("Ingresa el numero de interfaz: "))-1
interface_name = interfaces[read]

#cuando se elige configurar la red o agregar un nuevo usuario se ingresa a los routers mediante SSH
def init_configure(opcion,protocolo,opc,opt):
	con = ConnectHandler(**cisco)
	output = con.send_command("show running-config | i hostname")
	hostname = output.split()
	known_routers.append(hostname[1])

	#esta es la opcion cuando se quiere configurar la red con un protocolo
	if(opcion == 1):
		print ('¿Como quieres configurar la red?')
		protocolo=int(input('1 : RIP\n 2 : OSPF \n 3 : EIGRP\n'))

		if(protocolo==1):
			print(hostname[1]+":")
			rip(con)
			neighbors(hostname[1],con)
		elif(protocolo==2):
			print(hostname[1]+":")
			ospf(con)
			neighbors(hostname[1],con)
		elif(protocolo==3):
			print(hostname[1]+":")
			#eigrp(con)
			#neighbors(hostname[1],con)

	#esta es la opcion cuando se quiere agregar un nuevo usuario, este se va a agregar en toda la red
	elif(opcion == 3):
		usuarioNuevo = input('Ingresa el nombre de usuario: ')
		passwordNuevo = input('Ingresa la contraseña: ')
		opc=int(input('1: Agregar Usuario\n 2: Modificar Usuario\n 3: Borrar Usuario\n'))
		print(hostname[1]+":")
		if(opc==1):	
			agregarUsuario(con, usuarioNuevo, passwordNuevo)
			vecinos(hostname[1],con,usuarioNuevo,passwordNuevo,opc)
		elif(opc==2):
			modificarUsuario(con, usuarioNuevo, passwordNuevo)
			vecinos(hostname[1],con,usuarioNuevo,passwordNuevo,opc)
		elif(opc==3):
			borrarUsuario(con, usuarioNuevo, passwordNuevo)
			vecinos(hostname[1],con,usuarioNuevo,passwordNuevo,opc)

	elif(opcion == 4):
		ver=con.send_command("show version  | i Version ")
		tms=con.send_command("show version  | i uptime ")
		rver=ver.split(",")
		rtms=tms.split("is")
		print(hostname[1]+ ":")
		print("El dispositivo posee la version: " + rver[2])
		print("El dispositivo ha estado encendido: " + rtms[1])
		viewr(hostname[1],con)	
	elif(opcion == 5):
		print(hostname[1]+ ":")
		opt=int(input('Desea cambiar el hostname?\n 1: si\n 2:no,ver siguiente router '))
		if(opt==1):
			newname=input('Ingresa el nuevo hostname: \n')
			con.write_channel('configure terminal\n')
			comandn= "hostname "+newname
			print("Se ingresa: " +comandn)
			con.write_channel(comandn+'\n')
			time.sleep(1)
			con.write_channel('exit\n')
			time.sleep(1)
			vnh=con.send_command("show running-config | i hostname")
			nhn=vnh.split()
			print("El router se llama ahora: " + nhn[1])
		elif(opt==2):
			editr(hostname[1],con)
	con.disconnect()

#cuando se elige configurar la red con SSH se ingresa mediante telnet
def init_configureSSH():

	conT = ConnectHandler(**ciscot)

	output = conT.send_command("show running-config | i hostname")
	hostname = output.split()
	known_routers.append(hostname[1])

	#Pedimos los datos que se necesitan para los comandos de configuracion de SSH
	username = input('Ingresa el usuario que se configurara en la conexion SSH?: ')
	contraseña = input('Ingresa una contraseña: ')
	nombreDominio = input('Ingresa el nombre del dominio: ')
	numIntentos = input('Ingresa el numero de intentos para la conexion SSH: ')

	print(hostname[1]+":")
	ssh(con,nombreDominio,username,contraseña,numIntentos)
	neighborsTelnet(router,con,nombreDominio,username,contraseña,numIntentos)

	conT.disconnect()

def findRouter():
	dic_data=ni.ifaddresses(interface_name)
	dic_data=dic_data[2][0]
	    
	addr=list(map(int,dic_data["addr"].split(".")))
	net=list(map(int,dic_data["netmask"].split(".")))

	c=determinate_prefix(net)
	idnet=get_id_net(addr,net)
	range_net=get_broadcast_ip(idnet,net)

	print(f"Escaneando subred {arr_to_ip(idnet)}/{c}\n")

	ips=[idnet[0],idnet[1],idnet[2],idnet[3]+1]
	responde=scan_range(ips,range_net)

	for i in range(len(responde)):
	    for k,v in responde[i].items():
	        if "Router" in v:
	            return k

def neighbors(hostname,con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	routers.pop()
	i = 35
	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router(routers[i],hostname,con)
		i = i + 8

def configure_router(router,hostname,con):
	user = cisco['username']
	password = cisco['password']
	print(""+user)
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('ssh -l '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')

	#aqui va configurando los routers vecinos, hasta que no encuentre un router mas
	rip(con)
	#ospf(con)
	neighbors(router,con)

	print("HOSTNAME CONFIGURE:", hostname)
	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')

def viewr(hostname,con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	routers.pop()
	i = 35
	while i < len(routers):
		if routers[i] not in known_routers:
			nr=routers[i].split(".")
			print(nr[0]+":")
			known_routers.append(routers[i])
			configure_router_info(routers[i],hostname,con)
		i = i + 8

def editr(hostname,con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	routers.pop()
	i = 35
	while i < len(routers):
		if routers[i] not in known_routers:
			nr=routers[i].split(".")
			print(nr[0]+":")
			known_routers.append(routers[i])
			edit_router_info(routers[i],hostname,con)
		i = i + 8

def vecinos(hostname,con,usuarioNuevo,passwordNuevo,opc):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	routers.pop()
	i = 35
	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router_usuarios(routers[i],hostname,con,usuarioNuevo,passwordNuevo,opc)
		i = i + 8

def configure_router_usuarios(router,hostname,con,usuarioNuevo,passwordNuevo,opc):
	user = cisco['username']
	password = cisco['password']
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('ssh -l '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')
	if(opc==1):
		#aqui va agregando el nuevo usuario en los routers vecinos, hasta que ya no encuentre un router mas
		agregarUsuario(con,usuarioNuevo,passwordNuevo)
		vecinos(router,con,usuarioNuevo,passwordNuevo,opc)
	elif(opc==2):
		#aqui va modificando el nuevo usuario en los routers vecinos, hasta que ya no encuentre un router mas
		modificarUsuario(con,usuarioNuevo,passwordNuevo)
		vecinos(router,con,usuarioNuevo,passwordNuevo,opc)
	elif(opc==3):
		#aqui va borrando el nuevo usuario en los routers vecinos, hasta que ya no encuentre un router mas
		borrarUsuario(con,usuarioNuevo,passwordNuevo)
		vecinos(router,con,usuarioNuevo,passwordNuevo,opc)

	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')

#funcion que obtiene los datos del router y los imprime
def configure_router_info(router,hostname,con):
	user = cisco['username']
	password = cisco['password']
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('ssh -l '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')
	host=con.send_command("show running-config | i hostname ")
	sn= host.split()
	ver=con.send_command("show version  | i Version ")
	tms=con.send_command("show version  | i uptime ")
	rver=ver.split(",")
	rtms=tms.split("is")
	print("El dispositivo posee la version: " + rver[2])
	ftms= rtms[1].split(sn[1])
	print("El dispositivo ha estado encendido: " + ftms[0])

	#aqui va agregando el nuevo usuario en los routers vecinos, hasta que ya no encuentre un router mas
	#agregarUsuario(con,usuarioNuevo,passwordNuevo)
	#vecinos(router,con,usuarioNuevo,passwordNuevo)
	viewr(router,con)

	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')


def edit_router_info(router,hostname,con):
	user = cisco['username']
	password = cisco['password']
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('ssh -l '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')
	opte=int(input('Desea cambiar el hostname?\n 1: si\n 2:no,ver siguiente router '))
	if(opte==1):
		newname=input('Ingresa el nuevo hostname: \n')
		con.write_channel('configure terminal\n')
		comandn= "hostname "+newname
		print("Se ingresa: " +comandn)
		con.write_channel(comandn+'\n')
		time.sleep(1)
		con.write_channel('exit\n')
		time.sleep(1)
		vnh=con.send_command("show running-config | i hostname")
		nhn=vnh.split()
		print("El router se llama ahora: " + nhn[1])
	elif(opte==2):
		#aqui va agregando el nuevo usuario en los routers vecinos, hasta que ya no encuentre un router mas
		editr(router,con)
	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')



def neighborsTelnet(hostname,con,nombreDominio,username,contraseña,numIntentos):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	routers.pop()
	i = 35
	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router_telnet(routers[i],hostname,con,nombreDominio,username,contraseña,numIntentos)
		i = i + 8

def configure_router_telnet(router,hostname,con,nombreDominio,username,contraseña,numIntentos):
	user = ciscot['username']
	password = ciscot['password']
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('telnet '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')

	#aqui va configurando SSH en los routers vecinos, hasta que no encuentra ninguno
	ssh(con,nombreDominio,username,contraseña,numIntentos)
	neighborsTelnet(router,con,nombreDominio,username,contraseña,numIntentos)

	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')

def findNetworkID(ip,con):
	output = con.send_command('show ip interface brief | i '+ip)
	net = output.split()
	output = con.send_command('show running-config | i '+net[1])
	mask = output.split()

	addr=list(map(int,net[1].split(".")))
	netmask=list(map(int,mask[3].split(".")))

	idnet=get_id_net(addr,netmask)

	return arr_to_ip(idnet)

#este es el metodo con los comando para configurar RIP
def rip(con):
	output = con.send_command('show ip interface brief | i up')
	ip = output.split()
	
	ip_id = []
	i = 1
	while i < len(ip):
		ip_id.append(findNetworkID(ip[i],con))
		i = i + 6

	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel('router rip\n')
	time.sleep(1)
	con.write_channel('version 2\n')
	time.sleep(1)

	for i in ip_id:
		print('RIP Network '+i)
		con.write_channel('network '+i+'\n')
		time.sleep(1)

	con.write_channel('exit\n')
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)
#metodo base para ospf no funciona :'v
def ospf(con):
	output = con.send_command('show ip interface brief | i up')
	ip = output.split() 
	
	ip_id = []
	i = 1 
	while i < len(ip):
		ip_id.append(findNetworkID(ip[i],con))
		i = i + 6
	global sb
	global sbb
	opa= str(sb)
	opb= str(sbb)
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel('router ospf 200\n')
	time.sleep(1)
	con.write_channel('network 200.0.0.'+opa +  ' 255.255.255.255 area 0\n')
	time.sleep(1)
	con.write_channel('network 192.168.1.'+opb +  ' 0.0.0.255 area 0\n')
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)
	con.write_channel('exit\n')
	sb=sb+1
	sbb=sbb+1

#este es el metodo con los comandos para configurar SSH
def ssh(con,nombreDominio,username,contraseña,numIntentos):
	print("Se está configurando la conexión SSH...")

	con.write_channel("configure terminal")
	time.sleep(1)
	con.write_channel("ip domain-name "+nombreDominio)
	time.sleep(1)
	con.write_channel("username "+username+" privilege 15 password "+contraseña)
	time.sleep(1)
	con.write_channel("crypto key generate rsa")
	time.sleep(1)
	con.write_channel("1024")
	time.sleep(1)
	con.write_channel("ip ssh version 2")
	time.sleep(1)
	con.write_channel("ip ssh time-out 50")
	time.sleep(1)
	con.write_channel("ip ssh authentication-retries "+numIntentos)
	time.sleep(1)
	con.write_channel("service password-encryption")
	time.sleep(1)
	con.write_channel("line vty 0 15")
	time.sleep(1)
	con.write_channel("transport input ssh telnet")
	time.sleep(1)
	con.write_channel("password "+password)
	time.sleep(1)
	con.write_channel("login local")
	time.sleep(1)
	con.write_channel("end")
	time.sleep(1)
	con.write_channel("write")

	print("Se configuró la conexión SSH")

#este es el metodo con los comandos para agregar un nuevo usuario
def agregarUsuario(con, usuarioNuevo, passwordNuevo):
	print("Se está agregando un nuevo usuario...")
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel("username "+usuarioNuevo+" privilege 15 password "+passwordNuevo)
	print("Se agregó el nuevo usuario")
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)

#este es el metodo con los comandos para modificar un nuevo usuario
def modificarUsuario(con, usuarioNuevo, passwordNuevo):
	print("Se está modificando el usuario...")
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel("username "+usuarioNuevo+" privilege 15 password "+passwordNuevo)
	print("Se modificó el usuario")
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)

#este es el metodo con los comandos para borrar un nuevo usuario
def borrarUsuario(con, usuarioNuevo, passwordNuevo):
	print("Se está eliminando el usuario...")
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel("no username "+usuarioNuevo+" privilege 15 password "+passwordNuevo)
	print("Se eliminó el usuario")
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)
	con.write_channel('exit\n')
	time.sleep(1)


print('Elige lo que deseas realizar?\n')

opcion = int(input('1 : Configurar la red\n 2 : Configurar la conexión SSH de la red \n 3 : Agregar, modificar o eliminar un nuevo usuario\n 4: Ver informacion del dispositivo\n 5: Cambiar hostname\n'))

def switch(opcion,usuario,password)
	#configurar la red con un protocolo (RIP, OSPF o EIGRP)
	if(opcion==1):
		usuario = input('Ingresa tu nombre de usuario: ')
		cisco['username'] = usuario
		password = input('Ingresa tu contraseña: ')
		cisco['password'] = password

		ip = findRouter()
		print ('Router encontrado en '+ip)
		cisco['ip'] = ip

		init_configure(opcion)

	#configurar la conexion SSH mediante telnet
	elif(opcion==2):
		usuarioTelnet = input('Ingresa el nombre de usuario: ')
		ciscot['username'] = usuarioTelnet
		passwordTelnet = input('Ingresa tu contraseña: ')
		ciscot['password'] = passwordTelnet

		ipT = findRouter()
		print ('Router encontrado en '+ipT)
		ciscot['ip'] = ipT

		init_configureSSH()

	#agregar, modificar o eliminar un nuevo usuario a todos los routers
	elif(opcion==3):
		usuarioAdmin = input('Ingresa tu nombre de usuario: ')
		passwordAdmin = input('Ingresa tu password: ')
		cisco['username'] = usuarioAdmin
		cisco['password'] = passwordAdmin
		ipU = findRouter()
		print ('Router encontrado en '+ipU)
		cisco['ip'] = ipU

		init_configure(opcion)
	#Ver informacion de dispositivos
	elif(opcion==4):
		usuarioAdmin = input('Ingresa tu nombre de usuario: ')
		passwordAdmin = input('Ingresa tu password: ')
		cisco['username'] = usuarioAdmin
		cisco['password'] = passwordAdmin
		ipU = findRouter()
		print ('Router encontrado en '+ipU)
		cisco['ip'] = ipU
		init_configure(opcion)
	#Cambiar hostname
	elif(opcion==5):
		usuarioAdmin = input('Ingresa tu nombre de usuario: ')
		passwordAdmin = input('Ingresa tu password: ')
		cisco['username'] = usuarioAdmin
		cisco['password'] = passwordAdmin
		ipU = findRouter()
		print ('Router encontrado en '+ipU)
		cisco['ip'] = ipU
		init_configure(opcion)
