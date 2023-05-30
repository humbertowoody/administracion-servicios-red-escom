from ssh_connect import conectar
from enru import findNetworkID
from netmiko import ConnectHandler
from time import sleep

def obtener_enrutamiento_routers(hosts: list) -> list:
  # Instrucciones (comandos) para verificar el enrutamiento.
  instrucciones_obtener_enrutamiento = [
    'show running-config | i rip',
    'show running-config | i ospf',
    'show running-config | i eigrp',
  ]
  
  # Variable con el resultado.
  protocolos = []

  # Iteramos sobre todos los hosts.
  for host in hosts:
    # Preparamos los datos de conexión ssh.
    cisco = {
      "device_type": "cisco_xe",
      "ip": host["ip"], 
      "username": "admin", 
      "password": "admin01",
      "secret": "12345678" 
    }

    # Realizamos la conexión y los comandos.
    resultado = conectar(cisco, instrucciones_obtener_enrutamiento)

    # Imprimimos el resultado.
    print(f'Para host {host["hostname"]} el resultado es: {resultado}')

    # Guardamos el resultado
    protocolos.append({
      "hostname": host["hostname"],
      "rip": True if len(resultado[0]) > 0 else False,
      "ospf": True if len(resultado[1]) > 0 else False,
      "eigrp": True if len(resultado[2]) > 0 else False
    })

  # Regresamos los protocolos.
  return protocolos


def ospf(conexion: ConnectHandler):
  # Obtenemos las redes en las interfaces activas.
  output = conexion.send_command('show ip interface brief | i up')

  # Parseamos la salida.
  ip = output.split()
  
  # Para almacenar cada una de las redes
  ip_id = []

  # Iteramos sobre los resultados.
  i = 1
  while i < len(ip):
    # Calculamos los datos para la red.
    ip_id.append(findNetworkID(ip[i], conexion))

    # Aumentamos nuestro contador.
    i = i + 6

  # Preparamos los comandos.
  comandos_configuracion_ospf = [
    'configure terminal',
    'no ip routing',
    'ip routing',
    'router ospf 1'
  ]


  # Añadimos las redes
  for red in ip_id:
    comandos_configuracion_ospf.append(f'net {red["idRed"]} {red["wildcard"]} area 0')
  
  # Agregamos el fin de operación.
  comandos_configuracion_ospf.append('end')

  # Ejecutamos los comandos
  for comando in comandos_configuracion_ospf:
    print(conexion.send_command(comando))
    sleep(1)

def rip(conexion: ConnectHandler):
  # Obtenemos las redes en las interfaces activas.
  output = conexion.send_command('show ip interface brief | i up')

  # Parseamos la salida.
  ip = output.split()
  
  # Para almacenar cada una de las redes
  ip_id = []

  # Iteramos sobre los resultados.
  i = 1
  while i < len(ip):
    # Calculamos los datos para la red.
    ip_id.append(findNetworkID(ip[i], conexion))

    # Aumentamos nuestro contador.
    i = i + 6

  # Preparamos los comandos.
  comandos_configuracion_rip = [
    'no ip routing',
    'ip routing',
    'router rip',
    'version 2',
    'no auto-summary'
  ]

  # Añadimos las redes
  for red in ip_id:
    comandos_configuracion_rip.append(f'network {red["idRed"]}')
  
  # Enviamos los comandos al router.
  conexion.send_config_set(comandos_configuracion_rip)

def eigrp(conexion: ConnectHandler):
  # Obtenemos las redes en las interfaces activas.
  output = conexion.send_command('show ip interface brief | i up')

  # Parseamos la salida.
  ip = output.split()
  
  # Para almacenar cada una de las redes
  ip_id = []

  # Iteramos sobre los resultados.
  i = 1
  while i < len(ip):
    # Calculamos los datos para la red.
    ip_id.append(findNetworkID(ip[i], conexion))

    # Aumentamos nuestro contador.
    i = i + 6

  # Preparamos los comandos.
  comandos_configuracion_eigrp = [
    'no ip routing',
    'ip routing',
    'router eigrp 10',
    'no auto-summary'
  ]

  # Añadimos las redes
  for red in ip_id:
    comandos_configuracion_eigrp.append(f'net {red["idRed"]} {red["wildcard"]}')
  
  # Enviamos los comandos al router.
  conexion.send_config_set(comandos_configuracion_eigrp)

def actualizar_enrutamiento(hosts, enrutamiento):

  orden = ['ISP', 'Edge', 'TOR2', 'R2', 'R1', 'TOR1']

  orden = {key: i for i, key in enumerate(orden)}

  hosts_ordenados = sorted(hosts, key=lambda d: orden[d['hostname']])

  # Iteramos sobre cada router.
  for host in hosts_ordenados:
    print(f'Configurando {host["hostname"]}...')
    # Preparamos los datos de conexión ssh.
    cisco = {
      "device_type": "cisco_ios",
      "ip": host["ip"], 
      "username": "admin", 
      "password": "admin01",
      "secret": "12345678",
      #"read_timeout_override": 90
    }

    # Establecemos la conexión.
    conexion = ConnectHandler(**cisco)

    # Activamos el modo configuración.
    conexion.enable()

    # Actuamos según el protocolo seleccionado por el usuario.
    if enrutamiento == "RIP":
      rip(conexion)
    elif enrutamiento == "OSPF":
      ospf(conexion)
    elif enrutamiento == "EIGRP":
      eigrp(conexion)

    # print("Validando...")
    # print(conexion.send_command('show running-config | i rout'))
    # print(conexion.send_command('show running-config | i network'))
    # print("Cerrando conexión...")
    
    # # Cerramos la conexión.
    conexion.disconnect()

    print(f'Fin de configuración para {host["hostname"]}')
    break ########


