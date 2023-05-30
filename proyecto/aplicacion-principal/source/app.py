from flask import Flask, request, render_template, Response
from module_scan import scan_by_interface
from datetime import datetime
import json
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.secmod.rfc2576 import udp
from time import sleep
from threading import Thread
from dibujo import construirDibujoTopologia, copiar_archivos, eliminar, b64_img_de_metricas_router
from snmp import obtener_valor_oid, oid_para_uptime, oid_para_syscontact, oid_para_hostname, oid_para_syslocation, oid_para_sysdescription, oid_paquetes_entrantes_interfaz, oid_paquetes_salientes_interfaz, oid_paquetes_erroneos_interfaz, colocar_valor_oid
from constantes import COMUNIDAD_DEFAULT, PASS_GMAIL
from enrutamiento import obtener_enrutamiento_routers, actualizar_enrutamiento
import smtplib
from usuario import crear_usuario

# Inicializar la aplicación de Flask.
app = Flask(__name__)

# Variables globales.
tiempo_muestreo = 5
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
metricas_por_router = {}
usuarios_router = {}

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
    # Todo dentry de un try/catch
    try:
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

      # Mensajze de ejecución.
      print("Red escaneada correctamente")

      # Pausa de la menor cantidad de tiempo posible.
      sleep(tiempo_entre_escaneos.total_seconds())
    except:
      print("[ERROR] No se pudo escanear la red.")

# Función que cada X tiempo obtiene las métricas requeridas.
def funcion_hilo_obtener_metricas():
  # Variables globales usadas.
  global tiempo_muestreo
  global metricas_por_router
  global hosts

  # Ciclo infinito.
  while True:
    # Todo dentro de un try/catch.
    try:
      # Iteramos sobre los enrutadores.
      for enrutador in hosts:
        # Validamos que el enrutador esté en el diccionario.
        if enrutador["hostname"] not in metricas_por_router:
          # Creamos el diccionario vacío.
          metricas_por_router[enrutador["hostname"]] = {
            "1": {
              "fechas": [],
              "paquetes_entrantes": [],
              "paquetes_salientes": [],
              "paquetes_erroneos": []
            },
            "2": {
              "fechas": [],
              "paquetes_entrantes": [],
              "paquetes_salientes": [],
              "paquetes_erroneos": []
            },
            "3": {
              "fechas": [],
              "paquetes_entrantes": [],
              "paquetes_salientes": [],
              "paquetes_erroneos": []
            },
            "4": {
              "fechas": [],
              "paquetes_entrantes": [],
              "paquetes_salientes": [],
              "paquetes_erroneos": []
            },
            "5": {
              "fechas": [],
              "paquetes_entrantes": [],
              "paquetes_salientes": [],
              "paquetes_erroneos": []
            },
          }

        # Iteramos sobre las 5 interfaces.
        for interfaz in range(1,6):
          # Guardamos la fecha actual.
          metricas_por_router[enrutador["hostname"]][f'{interfaz}']["fechas"].append(datetime.now())

          # Paquetes entrantes.
          metricas_por_router[enrutador["hostname"]][f'{interfaz}']["paquetes_entrantes"].append(
            obtener_valor_oid(enrutador["ip"], COMUNIDAD_DEFAULT, oid_paquetes_entrantes_interfaz(interfaz))
          )

          # Paquetes salientes.
          metricas_por_router[enrutador["hostname"]][f'{interfaz}']["paquetes_salientes"].append(
            obtener_valor_oid(enrutador["ip"], COMUNIDAD_DEFAULT, oid_paquetes_salientes_interfaz(interfaz))
          )

          # Paquetes erróneos.
          metricas_por_router[enrutador["hostname"]][f'{interfaz}']["paquetes_erroneos"].append(
            obtener_valor_oid(enrutador["ip"], COMUNIDAD_DEFAULT, oid_paquetes_erroneos_interfaz(interfaz))
          )

      # Mensaje de ejecución
      print("Métricas obtenidas correctamente")

      # Pausa.
      sleep(tiempo_muestreo)
    except:
      # Mensaje de error.
      print(f"[ERROR] No se pudieron leer las métricas.")

      # Pausa
      sleep(tiempo_muestreo)

# Definición de la función de callback que se ejecutará por cada trap que recibamos.
def funcion_callback(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    # Imprimimos que se recibió un trap.
  print("Se recibió un trap de SNMP.")

  execContext = snmpEngine.observer.getExecutionContext(
        'rfc3412.receiveMessage:request'
    )

  print('Notification from %s:%s' % execContext['transportAddress'])

  print("varBinds:")
  
  # Iteramos sobre la información obtenida.
  for name, val in varBinds: 
        # Impresión de debug.
        print(f"\t- name: {name.prettyPrint()} ; valor: {val.prettyPrint()}")

        print ('Enviando mail...')

        # Email details
        sender_email = "humbertowoody@gmail.com"
        receiver_email = "humbertowoody@example.com"
        password = PASS_GMAIL
        message = f'Se detectó nuevo trap de SNMP: \n{json.dumps(varBinds, default=str, indent=4)}'

        # Send email
        server = smtplib.SMTP("1.1.1.1", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()

        print('Mail enviado!')

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
@app.route('/', methods=["GET"])
def inicio():
    return json.dumps({
        "materia": {
          "nombre": "Administración de Servicios en Red",
          "profesor": "Ricardo Martínez Rosales",
          "grupo": "4CM11"
        },
        "equipo": {
          "nombre": "ElectroAdictos",
          "integrantes": [
            "Godínez Morales Mario Sebastián",
            "González Barrientos Geovanni Daniel",
            "Gutiérrez Gómez Yohan Leonardo",
            "Ortega Alcocer Humberto Alejandro"
          ],
        },
        "fecha": str(datetime.now())
    }), 200, {'Content-Type': 'application/json'}

@app.route('/enrutadores', methods=["GET"])
def obtener_enrutadores():
  # Variables globales.
  global conexiones_r

  # Regresamos la información en formato JSON.
  return json.dumps(conexiones_r, default=str), 200, {'Content-Type': 'application/json'}

@app.route('/enrutadores/metricas', methods=["GET"])
def obtener_metricas_enrutadores():
  # Variables globales
  global metricas_por_router

  # Regresamos un JSON con las métricas hasta ahora.
  return json.dumps(metricas_por_router, default=str), 200, {'Content-Type': "application/json"}

@app.route('/enrutadores/<id>')
def obtener_enrutador(id: str):
  # Variables globales.
  global conexiones_r

  # Iteramos sobre cada enrutador
  for enrutador in conexiones_r:
    # Si encontramos el que especificó el usuario, lo regresamos.
    if enrutador["hostname"] == id:
      return json.dumps(enrutador), 200, {'Content-Type': 'application/json'}
  
  # Si no lo encontramos, 404.
  return json.dumps({"error": "el enrutador no existe o no ha sido detectado aún"}), 404, {'Content-Type': 'application/json'}

@app.route('/enrutadores/<id>/snmp', methods=["GET", "PUT"])
def enturador_snmp(id: str):
  # Variables globales
  global hosts

  # Iteramos sobre los hosts.
  for host in hosts:
    # Si encontramos el que especificó el usuario, calculamos sus datos.
    if host["hostname"] == id:
      # Si es GET...
      if request.method == "GET":
        return json.dumps({
          "uptime": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_uptime()),
          "hostname": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_hostname()),
          "sysContact": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syscontact()),
          "sysLocation": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syslocation()),
          "sysDescription": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_sysdescription()),
        }, default=str), 200, {'Content-Type': 'application-json'}
      # Si es un PUT...
      else:
        # Obtenemos el objeto serializado.
        objeto = request.get_json()

        # Actualizamos los valores.
        colocar_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syscontact(), str(objeto["sysContact"]))
        colocar_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syslocation(), str(objeto["sysLocation"]))

        # Devolvemos el resultado.
        return json.dumps({
          "uptime": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_uptime()),
          "hostname": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_hostname()),
          "sysContact": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syscontact()),
          "sysLocation": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_syslocation()),
          "sysDescription": obtener_valor_oid(host["ip"], COMUNIDAD_DEFAULT, oid_para_sysdescription()),
        }, default=str), 200, {'Content-Type': 'application-json'}
  
  # Si no lo encontramos, regresamos un error 404.
  return json.dumps({"error": "el enrutador no existe o no ha sido detectado aún"}), 404, {'Content-Type': 'application-json'}

@app.route('/enrutadores/<id>/metricas', methods=["GET"])
def obtener_metricas_enrutador(id: str):
  # Variables globales
  global metricas_por_router

  # Iteramos sobre las métricas buscando el ID.
  for enrutador in metricas_por_router:
    # Si el enrutador es el que especificó el usuario, regresamos sus datos.
    if enrutador == id:
      return json.dumps(metricas_por_router[enrutador], default=str), 200, {'Content-Type': 'application/json'}

  # Si no lo encontramos, 404.
  return json.dumps({"error": "el enrutador no existe o no ha sido detectado aún"})

@app.route('/enrutadores/<id>/metricas/grafica', methods=["GET"])
def obtener_grafica_metricas_enrutador(id: str):
  # Variables globales
  global metricas_por_router

  # Iteramos sobre las métricas buscando el ID.
  for enrutador in metricas_por_router:
    # Si el enrutador es el que especificó el usuario, regresamos sus datos.
    if enrutador == id:
      grafica_base64 = b64_img_de_metricas_router(metricas_por_router[enrutador], tiempo_muestreo, enrutador)
      return '<img src="data:image/png;base64,{}">'.format(grafica_base64)

  # Si no lo encontramos, 404.
  return json.dumps({"error": "el enrutador no existe o no ha sido detectado aún"})

@app.route('/enrutadores/<id>/usuarios', methods=["GET", "POST"])
def enrutador_usuarios(id: str):
  global hosts
  global usuarios_router

  for host in hosts:
    if host["hostname"] == id:
      if (request.method == 'POST'):
        usuario_nuevo = request.get_json()
        if id in usuarios_router.keys():
          usuarios_router[f'{id}'].append(usuario_nuevo)
        else:
          usuarios_router[f'{id}'] = [usuario_nuevo]
        return json.dumps(crear_usuario(host, usuario_nuevo)), 200, {'content-type': 'application/json'}
      else:
        if id in usuarios_router.keys():
          return json.dumps(usuarios_router[f'{id}']), 200, {'content-type': 'application/json'}
        else:
          return json.dumps([]), 200, {'Content-Type': 'application/json'}

  return json.dumps({'error': 'no se encontró el enrutador o no ha sido detectado'}), 404, {'content-type': 'application/json'}

@app.route('/enrutamiento', methods=["GET", "PUT"])
def enrutamiento():
  # Variables globales.
  global hosts

  # Si es un PUT, queremos actualizar el enrutamiento.
  if request.method == 'PUT':
    # Obtenemos el objeto.
    objeto = request.get_json()

    # Validamos si el objeto tiene la estructura que buscamos.
    if objeto["protocolo"]:
      # Validamos que el protocolo solicitado sea válido.
      if objeto["protocolo"] in ['RIP', 'EIGRP', 'OSPF']:
        # Imprimimos un manesaje
        print(f'Se solicitó cambiar el protocolo a: {objeto["protocolo"]}')

        # Actualizamos el protocolo.
        actualizar_enrutamiento(hosts, objeto["protocolo"])

        # Informamos al usuario.
        return json.dumps({"resultado": f'todos los routers ahora usan {objeto["protocolo"]}'}), 200, {'Content-Type': 'application/json'}
      else:
        return json.dumps({"error": "el protocolo especificado no existe"}), 400, {'Content-Type': 'application/json'}
    else:
      return json.dumps({"error": "la estructura del objeto enviado no se reconoce"}), 400, {'Content-Type': 'application/json'}
  else:
    return json.dumps(obtener_enrutamiento_routers(hosts), indent=4, default=str), 200, {'Content-Type': 'application/json'}

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
  Thread(target=funcion_hilo_escanear_red).start()
  Thread(target=funcion_hilo_traps).start()
  Thread(target=funcion_hilo_obtener_metricas).start()
  print("¡Hilos inicializados correctamente!")

# Ejecutamos la aplicacion.
if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0", port=5000)
