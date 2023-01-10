from flask import Flask, request, render_template, Response
from module_scan import scan_by_interface
from datetime import datetime
import json
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.secmod.rfc2576 import udp
from time import sleep
from threading import Thread
from dibujo import construirDibujoTopologia, copiar_archivos, eliminar


# Inicializar la aplicación de Flask.
app = Flask(__name__)

# Variables globales.
tiempo_muestreo = 30
conexiones_r = [
  {
    "hostname": "TOR1",
    "interfaces": [
      {
        "name": "FastEthernet0/0",
        "ip": "192.168.0.1",
        "netmask": "255.255.255.0",
        "idnet": "192.168.0.0/24"
      },
      {
        "name": "FastEthernet1/0",
        "ip": "10.10.10.18",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.16/30"
      },
      {
        "name": "FastEthernet1/1",
        "ip": "10.10.10.14",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.12/30"
      },
      {
        "name": "FastEthernet2/0",
        "ip": "192.168.1.1",
        "netmask": "255.255.255.0",
        "idnet": "192.168.1.0/24"
      }
    ]
  },
  {
    "hostname": "R1",
    "interfaces": [
      {
        "name": "FastEthernet0/0",
        "ip": "10.10.10.2",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.0/30"
      },
      {
        "name": "FastEthernet1/0",
        "ip": "10.10.10.17",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.16/30"
      },
      {
        "name": "FastEthernet1/1",
        "ip": "10.10.10.9",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.8/30"
      }
    ]
  },
  {
    "hostname": "R2",
    "interfaces": [
      {
        "name": "FastEthernet0/0",
        "ip": "10.10.10.6",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.4/30"
      },
      {
        "name": "FastEthernet1/0",
        "ip": "10.10.10.21",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.20/30"
      },
      {
        "name": "FastEthernet1/1",
        "ip": "10.10.10.13",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.12/30"
      }
    ]
  },
  {
    "hostname": "Edge",
    "interfaces": [
      {
        "name": "FastEthernet0/0",
        "ip": "20.20.30.2",
        "netmask": "255.255.255.252",
        "idnet": "20.20.30.0/30"
      },
      {
        "name": "FastEthernet1/0",
        "ip": "10.10.10.1",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.0/30"
      },
      {
        "name": "FastEthernet1/1",
        "ip": "10.10.10.5",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.4/30"
      }
    ]
  },
  {
    "hostname": "TOR2",
    "interfaces": [
      {
        "name": "FastEthernet1/0",
        "ip": "10.10.10.22",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.20/30"
      },
      {
        "name": "FastEthernet1/1",
        "ip": "10.10.10.10",
        "netmask": "255.255.255.252",
        "idnet": "10.10.10.8/30"
      },
      {
        "name": "FastEthernet2/0",
        "ip": "192.168.10.1",
        "netmask": "255.255.255.0",
        "idnet": "192.168.10.0/24"
      },
      {
        "name": "FastEthernet2/1",
        "ip": "192.168.11.1",
        "netmask": "255.255.255.0",
        "idnet": "192.168.11.0/24"
      }
    ]
  },
  {
    "hostname": "ISP",
    "interfaces": [
      {
        "name": "FastEthernet0/0",
        "ip": "20.20.30.1",
        "netmask": "255.255.255.252",
        "idnet": "20.20.30.0/30"
      },
      {
        "name": "FastEthernet1/0",
        "ip": "20.20.20.1",
        "netmask": "255.255.255.0",
        "idnet": "20.20.20.0/24"
      }
    ]
  }
]
arr_interconexiones = [
  "TOR1-R1:10.10.10.16",
  "TOR1-R2:10.10.10.12",
  "R1-Edge:10.10.10.0",
  "R1-TOR2:10.10.10.8",
  "R2-Edge:10.10.10.4",
  "R2-TOR2:10.10.10.20",
  "Edge-ISP:20.20.30.0"
]
net_router = {
  "TOR1": {
    "FastEthernet0/0": "192.168.0.1/24",
    "FastEthernet1/0": "10.10.10.18/30",
    "FastEthernet1/1": "10.10.10.14/30",
    "FastEthernet2/0": "192.168.1.1/24"
  },
  "R1": {
    "FastEthernet0/0": "10.10.10.2/30",
    "FastEthernet1/0": "10.10.10.17/30",
    "FastEthernet1/1": "10.10.10.9/30"
  },
  "R2": {
    "FastEthernet0/0": "10.10.10.6/30",
    "FastEthernet1/0": "10.10.10.21/30",
    "FastEthernet1/1": "10.10.10.13/30"
  },
  "Edge": {
    "FastEthernet0/0": "20.20.30.2/30",
    "FastEthernet1/0": "10.10.10.1/30",
    "FastEthernet1/1": "10.10.10.5/30"
  },
  "TOR2": {
    "FastEthernet1/0": "10.10.10.22/30",
    "FastEthernet1/1": "10.10.10.10/30",
    "FastEthernet2/0": "192.168.10.1/24",
    "FastEthernet2/1": "192.168.11.1/24"
  },
  "ISP": {
    "FastEthernet0/0": "20.20.30.1/30",
    "FastEthernet1/0": "20.20.20.1/24"
  }
}
responde = [
  { "192.168.0.1": "Cisco_Router_IOS 0" },
  { "192.168.0.10": "Unix-OS 0" },
  { "192.168.0.11": "Unix-OS 0" },
  { "10.10.10.18": "Cisco_Router_IOS 0" },
  { "10.10.10.17": "Cisco_Router_IOS 1" },
  { "10.10.10.14": "Cisco_Router_IOS 0" },
  { "10.10.10.13": "Cisco_Router_IOS 1" },
  { "192.168.1.1": "Cisco_Router_IOS 0" },
  { "192.168.1.10": "Unix-OS 1" },
  { "10.10.10.2": "Cisco_Router_IOS 1" },
  { "10.10.10.1": "Cisco_Router_IOS 2" },
  { "10.10.10.9": "Cisco_Router_IOS 1" },
  { "10.10.10.10": "Cisco_Router_IOS 2" },
  { "10.10.10.6": "Cisco_Router_IOS 1" },
  { "10.10.10.5": "Cisco_Router_IOS 2" },
  { "10.10.10.21": "Cisco_Router_IOS 1" },
  { "10.10.10.22": "Cisco_Router_IOS 2" },
  { "20.20.30.2": "Cisco_Router_IOS 2" },
  { "20.20.30.1": "Cisco_Router_IOS 3" },
  { "10.10.10.6": "Cisco_Router_IOS 1" },
  { "10.10.10.5": "Cisco_Router_IOS 2" },
  { "10.10.10.21": "Cisco_Router_IOS 1" },
  { "10.10.10.22": "Cisco_Router_IOS 2" },
  { "192.168.10.1": "Cisco_Router_IOS 2" },
  { "192.168.10.10": "Unix-OS 3" },
  { "192.168.11.1": "Cisco_Router_IOS 2" },
  { "192.168.11.10": "Unix-OS 3" },
  { "192.168.11.11": "Unix-OS 3" },
  { "20.20.20.1": "Cisco_Router_IOS 3" },
  { "20.20.20.20": "Unix-OS 4" }
]
hosts = [
  { "hostname": "TOR1", "ip": "192.168.1.1" },
  { "hostname": "R1", "ip": "10.10.10.9" },
  { "hostname": "R2", "ip": "10.10.10.13" },
  { "hostname": "Edge", "ip": "10.10.10.5" },
  { "hostname": "TOR2", "ip": "192.168.11.1" },
  { "hostname": "ISP", "ip": "20.20.20.1" }
]


# Función que escanea la red cada X tiempo.
def funcion_hilo_escanear_red():
  # Variables globales usadas.
  global conexiones_r
  global arr_interconexiones
  global net_router
  global responde
  global hosts

  # Variables locales.
  tiempo_entre_escaneos = 300 # Default de 5 minutos.

  # Ciclo infinito
  while True:
    # Medimos tiempo de inicio.
    inicio = datetime.now()

    # Escaneamos la red.
    resultado = scan_by_interface("eth0", "admin", "admin01", "12345678")

    # Medimos tiempo de fin.
    fin = datetime.now()

    # Ajustamos el tiempo de recorrido a la duración de la última ejecución.
    tiempo_entre_escaneos = fin - inicio

    # Ajustamos los datos.
    conexiones_r = resultado[0]
    arr_interconexiones = resultado[1]
    net_router = resultado[2]
    responde = resultado[3]
    hosts = resultado[4]

    # Pausa de 5 minutos.
    sleep(tiempo_entre_escaneos.total_seconds() + 30)

# Función que cada X tiempo obtiene las métricas requeridas.
def funcion_hilo_obtener_metricas():
  # Variables globales usadas.
  global tiempo_muestreo

  # Ciclo infinito.
  while True:
    # Obtenemos la hora actual.
    ahora = datetime.now()

    # Obtenemos la métrica actual.

    # Agregamos la fecha a nuestro arreglo.

    # Pausa.
    sleep(tiempo_muestreo)


# Definición de la función de callback que se ejecutará por cada
# trap que recibamos.
def funcion_callback(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    # Imprimimos que se recibió un trap.
  print("Se recibió un trap de SNMP.")
  
  # Iteramos sobre la información obtenida.
  # for name, val in varBinds: 
  #       # Impresión de debug.
  #       print(f"Debug trap: {name.prettyPrint()} : {val.prettyPrint()}")
  
  #       # Verificamos si está caída.
  #       if val.prettyPrint() == "administratively down":
  #         # Está caída
  #         estados.append(0) 

  #         # Guardamos la fecha actual.
  #         fechas_traps.append(datetime.now())

  #       elif val.prettyPrint() == "up":
  #         # Está levantada
  #         estados.append(1)

  #         # Guardamos la fecha actual.
  #         fechas_traps.append(datetime.now())

# Función para el hilo que captura los traps.
def funcion_hilo_traps():
    # Creamos el engine a utilizar.
    snmpEngine = engine.SnmpEngine()

    # Realizamos la configuración de transporte.
    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode(('192.168.0.10',162))
    )
    
    #Configuracion de comunidad V1 y V2c
    config.addV1System(snmpEngine, 'vista_proyecto', 'comunidad_proyecto')
  
    # Configuramos nuestra función de callback para cada dato recibido.
    ntfrcv.NotificationReceiver(snmpEngine, funcion_callback)

    # Iniciamos el trabajo de escucha de traps.	
    snmpEngine.transportDispatcher.jobStarted(1)  
  
    # Iniciamos el trabajo dentro de un try/catch.
    try:
        # Ejecutamos la tarea.
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        # Si ocurre una excepción, cerramos el hilo.
        snmpEngine.transportDispatcher.closeDispatcher()

        # Levantamos la excepción.
        raise
    
    # Finalizamos ejecución de la función.
    return 

# Ruta principal.
@app.route('/')
def inicio():
    return json.dumps({
        "materia": {
          "nombre": "Administración de Servicios en Red",
          "profesor": "Ricardo Martínez Rosales",
          "grupo": "4CM11"
        },
        "equipo": {
          "nombre": "electroadictos",
          "integrantes": [
            "Godínez Morales Mario Sebastián",
            "González Barrientos Geovanni Daniel",
            "Gutiérrez Gómez Yohan Leonardo",
            "Ortega Alcocer Humberto Alejandro"
          ],
        },
        "fecha": str(datetime.now())
    }), 200, {'Content-Type': 'application/json'}

@app.route('/enrutadores')
def obtener_enrutadores():
  global conexiones_r
  return json.dumps(conexiones_r), 200, {'Content-Type': 'application/json'}

@app.route('/enrutadores/<id>')
def obtener_enrutador(id: str):
  global conexiones_r
  for enrutador in conexiones_r:
    if enrutador["hostname"] == id:
      return json.dumps(enrutador), 200, {'Content-Type': 'application/json'}
    
  return json.dumps({"error": "el enrutador no existe o no ha sido detectado aún"}), 404, {'Content-Type': 'application/json'}

@app.route('/enrutadores/<id>/snmp', methods=["GET", "PUT"])
def enturador_snmp(id: str):
  return f"obteniendo snmp para {id}"

@app.route('/enrutadores/<id>/usuarios', methods=["GET", "POST", "PUT"])
def enrutador_usuarios(id: str):
  return "usuarios"

@app.route('/enrutadores/<id>/alertas', methods=["GET", "PUT"])
def enrutador_alertas(id: str):
  return "alertas"

@app.route('/enrutamiento', methods=["GET", "PUT"])
def enrutamiento():
  return "enrutamiento"


@app.route("/topologia")
def obtener_topologia():
  # Variables globales
  global conexiones_r
  global arr_interconexiones
  global net_router
  global responde
  global hosts

  # Construimos la topología
  net = construirDibujoTopologia(net_router, arr_interconexiones, responde, conexiones_r)
  net.save_graph("topologia.html")
  copiar_archivos("topologia.html", "/app/templates/topologia.html")
  eliminar("topologia.html")
  return render_template("topologia.html"), 200, {'Content-Type': 'text/html; charset=utf-8'}


#########   estos endpoints son para debug!

@app.route('/conexiones_r')
def obtener_conexiones_r():
  global conexiones_r
  return json.dumps(conexiones_r), 200

@app.route('/net_router')
def obtener_net_router():
  global net_router
  return json.dumps(net_router), 200

@app.route('/responde')
def obtener_responde():
  global responde
  return json.dumps(responde), 200

@app.route('/hosts')
def obtener_hosts():
  global hosts
  return json.dumps(hosts), 200

@app.route('/arr_interconexiones')
def obtener_arr_interconexiones():
  global arr_interconexiones
  return json.dumps(arr_interconexiones), 200

########################

@app.errorhandler(404)
def no_existe(error):
  return json.dumps({"error": "la url no existe"}), 404

@app.errorhandler(500)
def error_inesperado(error):
  return json.dumps({"error": "error inesperado"}), 500

# Iniciamos los hilos para consultar información.
@app.before_first_request
def iniciar_hilos():
  # Iniciamos los hilos...
  print("Inicializando hilos para escuchar información...")
  Thread(target=funcion_hilo_escanear_red).start()
  print("\t- Listo hilo para escanear la red.")
  Thread(target=funcion_hilo_traps).start()
  print("\t- Listo hilo para escuchar traps snmp.")
  Thread(target=funcion_hilo_obtener_metricas).start()
  print("\t- Listo hilo para consultar recurrentemente las métricas snmp seleccionadas.")
  print("¡Hilos inicializados correctamente!")

# Ejecutamos la aplicacion.
if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=5000)
