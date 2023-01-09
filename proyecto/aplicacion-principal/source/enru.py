from netmiko import ConnectHandler
#from ssh_connect import *
from detecta import *
import netifaces as ni
import time
import os

user = 'admin'
password = 'admin01'
secret = '12345678'

cisco = {
    "device_type": "cisco_ios",
    'ip': '',
    "username": user,
    "password": password,
    "secret": secret
}

known_routers = []


def arr_to_ip(ip):
	return f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"


def get_id_net(ip, net):
	idnet = []
	for i in range(4):
		idnet.append((ip[i] & net[i]))
	return idnet

def configure_router_rip(router,hostname,con):
#	user = cisco['username']
#	password = cisco['password']
#	print(""+user)
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	con.send_command('ssh -l '+user+' '+resp[8],expect_string=r'Password:')
	#aqui cambie quite la parte de send_command por la de write_channel y le quite la parte de expect_string
	#con.send_command(password, expect_string=r''+router+'#') ---> este es como estaba antes :v
	con.write_channel(password+'\n')

	#aqui va configurando los routers vecinos, hasta que no encuentre un router mas
	rip(con)
	#ospf(con)
	neighbors_rip(router,con)

	print("HOSTNAME CONFIGURE:", hostname)
	#esto de abajo lo cambie como esta en el de rip_ssh.py
	con.send_command('exit',expect_string=hostname.split(".")[0]+'#')

def configure_router_ospf(router, hostname, con):
    output = con.send_command(f'show cdp entry {router}')
    resp = output.split()
    comando_ssh = 'ssh -l '+user+' '+resp[8]
    # print("COMANDO:", comando_ssh)
    print("expect password")
    con.send_command(comando_ssh, expect_string=r'Password:')
    string_final = router.split(".")[0]
    print("string_final:", string_final)
    con.write_channel(password+'\n')
    # con.send_command(password, expect_string=r''+string_final+'#')

    ospf(con)

    neighbors_ospf(router, con)
    print("HOSTNAME CONFIGURE:", hostname)
    print("expect hostname")
    con.send_command('exit', expect_string=hostname.split(".")[0]+'#')
    return 1

def configure_router_eigrp(router, hostname, con):
	output = con.send_command(f'show cdp entry {router}')
	resp = output.split()
	comando_ssh = 'ssh -l '+user+' '+resp[8]
	# print("COMANDO:", comando_ssh)
	print("expect password")
	con.send_command(comando_ssh, expect_string=r'Password:')
	string_final = router.split(".")[0]
	print("string_final:", string_final)
	con.write_channel(password+'\n')
	# con.send_command(password, expect_string=r''+string_final+'#')

	eigrp(con)

	neighbors_eigrp(router, con)
	print("HOSTNAME CONFIGURE:", hostname)
	print("expect hostname")
	con.send_command('exit', expect_string=hostname.split(".")[0]+'#')
	return 1

def neighbors_eigrp(hostname, con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	# print("ROUTERS:",routers);
	routers.pop()
	# print("ROUTERS 2:",routers[35])
	# exit(1);

	i = 35
	global known_routers;

	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router(routers[i], hostname, con)
		i = i + 8
	return 1

def neighbors_ospf(hostname, con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	# print("ROUTERS:",routers);
	routers.pop()
	# print("ROUTERS 2:",routers[35])
	# exit(1);

	i = 35
	global known_routers;

	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router_ospf(routers[i], hostname, con)
		i = i + 8
	return 1

def neighbors_rip(hostname, con):
	output = con.send_command('show cdp neighbors')
	routers = output.split()
	# print("ROUTERS:",routers);
	routers.pop()
	# print("ROUTERS 2:",routers[35])
	# exit(1);

	i = 35
	global known_routers;

	while i < len(routers):
		if routers[i] not in known_routers:
			print(routers[i]+":")
			known_routers.append(routers[i])
			configure_router_rip(routers[i], hostname, con)
		i = i + 8
	return 1

def get_wildcard(mascara):
	wild = []
	mask = []

	for octeto in mascara:
		mask.append(str(octeto))

	ip = ".".join(mask)

	nip = ip.split(".")
	for i in range(4):
		wild.append(str(255-int(nip[i])))

	return{
		"wildcard": ".".join(wild),
		"mask": ip
	}


def findNetworkID(ip, con):
	output = con.send_command('show ip interface brief | i '+ip)
	net = output.split()
	output = con.send_command('show running-config | i '+net[1])
	mask = output.split()

	addr = list(map(int, net[1].split(".")))
	netmask = list(map(int, mask[3].split(".")))
	idnet = get_id_net(addr, netmask)
	identificadorRed = arr_to_ip(idnet)
	# print("identificadorRed:", identificadorRed)
	# print("netmask:", netmask)
	mask_wild = get_wildcard(netmask)

	return {
		"idRed": identificadorRed,
		"mascara": mask_wild["mask"],
		"wildcard": mask_wild["wildcard"]
	}

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
	con.write_channel('no ip routing\n')
	time.sleep(5)
	con.write_channel('ip routing\n')
	time.sleep(2)
	con.write_channel('router rip\n')
	time.sleep(1)
	con.write_channel('version 2\n')
	time.sleep(1)
	con.write_channel('no auto-summary\n')
	time.sleep(2)

	for i in range(len(ip_id)):
		print('RIP Network '+ip_id[i]["idRed"])
		con.write_channel('network '+ip_id[i]["idRed"]+'\n')
		time.sleep(1)

	output = con.write_channel('exit\n')
	time.sleep(1)
	output = con.write_channel('exit\n')
	time.sleep(1)

def ospf(con):
	output = con.send_command('show ip interface brief | i up')
	ip = output.split()
	# print("SH IP INT BR:",ip);
	ip_id = []
	i = 1
	while i < len(ip):
		ip_id.append(findNetworkID(ip[i], con))
		i = i + 6

	print("ip_ids:", ip_id)
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel('no ip routing\n')
	time.sleep(5)
	con.write_channel('ip routing\n')
	time.sleep(2)
	con.write_channel('router ospf 1\n')
	time.sleep(1)

	for i in ip_id:
		comando_ospf = 'net '+i["idRed"]+" "+i["wildcard"]+" area 0"+'\n'
		print('COMANDO OSPF:', comando_ospf)
		con.write_channel(comando_ospf)
		time.sleep(1)

	con.write_channel('exit\n')
	time.sleep(2)
	con.write_channel('exit\n')
	time.sleep(2)
	return 1

def eigrp(con):
	output = con.send_command('show ip interface brief | i up')
	ip = output.split()
	# print("SH IP INT BR:",ip);
	ip_id = []
	i = 1
	while i < len(ip):
		ip_id.append(findNetworkID(ip[i], con))
		i = i + 6

	print("ip_ids:", ip_id)
	con.write_channel('configure terminal\n')
	time.sleep(1)
	con.write_channel('no ip routing\n')
	time.sleep(5)
	con.write_channel('ip routing\n')
	time.sleep(2)
	con.write_channel('no auto-summary\n')
	time.sleep(2)
	con.write_channel('router eigrp  10\n')
	time.sleep(2)

	for i in ip_id:
		comando_eigrp = 'net '+i["idRed"]+" "+i["wildcard"]+'\n'
		print('COMANDO EIGRP:', comando_eigrp)
		con.write_channel(comando_eigrp)
		time.sleep(1)

	con.write_channel('exit\n')
	time.sleep(2)
	con.write_channel('exit\n')
	time.sleep(2)
	return 1

def init_rip_ssh(ip, userName, userPassword, secretP="12345678"):
    codigo = 0
    try:
        global known_routers;
        global user;
        user=userName;
        global password;
        password=userPassword;
        global secret;
        secret=secretP;
        cisco['ip'] = ip
        cisco['username'] = userName
        cisco['password'] = userPassword
        cisco['secret'] = secretP
        con = ConnectHandler(**cisco)
        output = con.send_command("show running-config | i hostname")
        hostname = output.split()
        print("HOSTNAME", hostname)
        known_routers.append(hostname[1])
        print(hostname[1]+":")
        rip(con)
        neighbors_rip(hostname[1], con)
        con.disconnect()
    except Exception as e:
        print("ERRORRR:", str(e))
        codigo = -1
    return {
        "codigoResultado": codigo
    }

def init_ospf_ssh(ip, userName, userPassword, secretP="12345678"):
    codigo = 0
    try:
        global known_routers;
        global user;
        user=userName;
        global password;
        password=userPassword;
        global secret;
        secret=secretP;
        cisco['ip'] = ip
        cisco['username'] = userName
        cisco['password'] = userPassword
        cisco['secret'] = secretP
        con = ConnectHandler(**cisco)
        output = con.send_command("show running-config | i hostname")
        hostname = output.split()
        print("HOSTNAME", hostname)
        known_routers.append(hostname[1])
        print(hostname[1]+":")
        ospf(con)
        neighbors_ospf(hostname[1], con)
        con.disconnect()
    except Exception as e:
        print("ERRORRR:", str(e))
        codigo = -1
    return {
        "codigoResultado": codigo
    }

def init_eigrp_ssh(ip, userName, userPassword, secretP="12345678"):
	codigo = 0
	try:
		global known_routers;
		global user;
		user=userName;
		global password;
		password=userPassword;
		global secret;
		secret=secretP;
		cisco['ip'] = ip
		cisco['username'] = userName
		cisco['password'] = userPassword
		cisco['secret'] = secretP
		con = ConnectHandler(**cisco)
		output = con.send_command("show running-config | i hostname")
		hostname = output.split()
		print("HOSTNAME", hostname)
		known_routers.append(hostname[1])
		print(hostname[1]+":")
		eigrp(con)
		neighbors_eigrp(hostname[1], con)
		con.disconnect()
	except Exception as e:
		print("ERRORRR:", str(e))
		codigo = -1
	return {
		"codigoResultado": codigo
	}
