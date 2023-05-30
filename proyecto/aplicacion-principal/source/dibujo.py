from pyvis.network import Network
import ipaddress, os
import matplotlib
matplotlib.use('Agg') # Usamos un renderizador Agg que no requiere UI.
import matplotlib.pyplot as plt
import base64
import io

def convertir_contadores_paquetes_en_lista(datos: list) -> list:
  # Variable con el resultado
  resultado = []

  # Iteramos sobre cada elemento en la lista.
  for i in range(len(datos)):
    # Si es el primer dato.
    if i == 0:
      # Si es el primer dato y solo hay un dato.
      if len(datos) == 1:
        resultado.append(0)
      # Si es el primer dato pero no hay un solo dato.
      else:
        resultado.append(datos[i+1] - datos[i])
    # Si no es el primer dato.
    else:
      resultado.append(datos[i] - datos[i-1])

  # Regresamos el arreglo resultante.
  return resultado

def b64_img_de_metricas_router(metricas_router, tiempo_muestreo: int, nombre_router: str) -> str:
  # Ajustamos el formato de la fecha a mostrar en la gráfica.
  plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"

  # Generamos el contenedor para la imágen.
  img = io.BytesIO()

  # Iteramos sobre cada enrutador.
  for interfaz in metricas_router:
    # Obtenemos las fechas.
    fechas = metricas_router[f'{interfaz}']["fechas"]

    # Obtenemos sus métricas actuales.
    paquetes_entrantes =  convertir_contadores_paquetes_en_lista(metricas_router[f'{interfaz}']["paquetes_entrantes"])
    paquetes_salientes =  convertir_contadores_paquetes_en_lista(metricas_router[f'{interfaz}']["paquetes_salientes"])
    paquetes_erroneos =  convertir_contadores_paquetes_en_lista(metricas_router[f'{interfaz}']["paquetes_erroneos"])
    
    # Creamos el plot para cada métrica de esta interfaz.
    plt.plot(fechas, paquetes_entrantes, label=f'Interfaz #{interfaz}- entrantes')
    plt.plot(fechas, paquetes_salientes, label=f'Interfaz #{interfaz}- salientes')
    plt.plot(fechas, paquetes_erroneos, label=f'Interfaz #{interfaz}- erróneos')
    
  # Ubicamos la leyenda arriba a la izquierda.
  plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
  
  # Activamos el grid.
  plt.grid()

  # Giramos las etiquetas 45°
  plt.xticks(rotation=45)

  # Título de la gráfica
  plt.title(f'Métricas de {nombre_router}')

  # Etiqueta para eje Y
  plt.ylabel(f'# de paquetes cada {tiempo_muestreo}s')

  # Guardamos la figura como PNG
  plt.savefig(img, format='png', bbox_inches="tight")

  # Regresamos el cursor del contenido.
  img.seek(0)

  # Creamos la gráfica en base64
  grafica_base64 = base64.b64encode(img.getvalue()).decode()

  # Limpiamos la gráfica.
  plt.clf()

  # Regresamos la imagen en base64.
  return grafica_base64

def copiar_archivos(net, out_net):
    #se cambia el link y script a referencia local
    fp = open(net, "r")
    fo = open(out_net, "w")
    for i in enumerate(fp):
        if i[0] == 2: 
            fo.write("<link rel='stylesheet' href='{{url_for('static',filename='pyvis_resources/vis.css')}}' type='text/css' />\n")
        elif i[0] == 3:
            fo.write("<script type='text/javascript' src='{{url_for('static',filename='pyvis_resources/vis-network.min.js')}}'></script>\n")
        else:
          fo.write(i[1])
    fp.close()
    fo.close()

def eliminar(file):
  os.remove(file)

def conexionesCli2edges(general_net, clients_dic, clients_id, routers_dic):
  edges = [] 
  nets = []
  for router in general_net:
    for interface in router["interfaces"]:
      red = interface["idnet"]
      for client, os in clients_dic.items():
        an_address = ipaddress.ip_address(client)
        a_network = ipaddress.ip_network(red)
        if an_address in a_network:
          edges.append((routers_dic[router["hostname"]], clients_id[client]))
          nets.append(red)
  return edges, nets


def client2Id(clients_dic, i):
  clients_id = {}
  j = i
  for client in clients_dic:
    clients_id[client] = j
    j += 1
  return clients_id

def devices2devicesDic(devices):
  dicDispositivos = {}
  for device in devices:
    for key in device:
      dicDispositivos[key] = device[key]
  return dicDispositivos

def obtenerDispositivos(devices):
  interfaces = {}
  clients = {}
  for ip, dis_type in devices.items():
    if "Cisco_Router_IOS" in dis_type:
      interfaces[ip] = dis_type
    else:
      clients[ip] = dis_type
  return interfaces, clients

def routers2routersDic(routers):
  routers_dic = {} 
  i = 0
  for router in routers:
    routers_dic[router] = i
    i+=1
  return routers_dic

def conexiones2edges(interconexiones, routers_dic):
  edges = []
  nets = []
  for interconexion in interconexiones:
    #separar routers
    router1 = interconexion.split(":")[0].split("-")[0]
    router2 = interconexion.split(":")[0].split("-")[1]
    net = interconexion.split(":")[1]
    edges.append((routers_dic[router1], routers_dic[router2]))
    nets.append(net)
  return edges, nets

def construirDibujoTopologia(routers, interconexiones, devices, general):
  routers_dic = routers2routersDic(routers)
  edges, redes = conexiones2edges(interconexiones, routers_dic)

  devices_dic = devices2devicesDic(devices)
  interfaces_dic, clients_dic = obtenerDispositivos(devices_dic)
  clients_id = client2Id(clients_dic, len(routers_dic))

  edges_cli, redes_cli = conexionesCli2edges(general, clients_dic, clients_id, routers_dic)

  net = Network()

  #nodos de cada router
  for router in routers_dic:
    print("anadiendo nodo router {}".format(router))
#		net.add_node(routers_dic[router], "{}".format(router), physics=False,mass=1, level=1, shape="image", title="interfaces:", image="{{ router }}")
    net.add_node(routers_dic[router], "{}".format(router), physics=False,mass=1, level=1, shape="image", title="interfaces:", image="static/blue/router.svg")

  #conexiones entre routers
  for (edge, red) in zip(edges, redes):
    print("anadiendo edge router {}".format(edge))
    net.add_edge(*edge, title=red)


  #nodos de cada cliente
  for client, id_cli in clients_id.items():
    print("anadiendo nodo cli {}".format(client))
#		net.add_node(id_cli, "{}".format(client), physics=False, mass=1, level=3, shape="image", title="{}".format(clients_dic[client]), image="{{ cliente }}")
    net.add_node(id_cli, "{}".format(client), physics=False, mass=1, level=3, shape="image", title="{}".format(clients_dic[client]), image="static/blue/client.svg")

  #conexiones de clientes
  for (edge, red) in zip(edges_cli, redes_cli):
    print("anadiendo edge cli {}".format(edge))
    net.add_edge(*edge, title=red)

  return net
