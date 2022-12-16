# app.py
# En este archivo se encuentra la definición de nuestra aplicación de Flask.
from flask import Flask, render_template
from pygal import Line
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.proto.secmod.rfc2576 import udp
from .conteo_paquetes import obtener_conteo # La función que obtiene el conteo de paquetes.
from time import sleep
from datetime import datetime
from threading import Thread


# Inicializamos flask.
app = Flask(__name__)

# Variables con los datos y fechas.
# OJO: Esto es una pésima idea y solo es con fines didácticos porque, oh dios,
#      primero que nada: race conditions. Y no hablemos del hecho de que Flask
#      levanta hilos *por request*, imagínense. Debería ser un archivo, o una 
#      base de datos, o algo pero, la neta, son las 11:30pm y ¯\_(ツ)_/¯
fechas_conteos = [] 
conteos = []
fechas_traps = []
estados = []

# Definición de la función que estará obteniendo los conteos para las gráficas.
def funcion_hilo_obtener_conteo():
    # Ciclo infinito.
    while True:
        # Obtenemos la hora actual.
        ahora = datetime.now()

        # Obtenemos el conteo actual de paquetes.
        conteo = obtener_conteo()

        # Agregamos la fecha a nuestro arreglo.
        fechas_conteos.append(ahora)

        # Agregamos el conteo a nuestro arreglo.
        conteos.append(conteo)

        # Pausa de 5 segundos.
        sleep(5)

# Definición de la función de callback que se ejecutará por cada
# trap que recibamos.
def funcion_callback(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    # Imprimimos que se recibió un trap.
	print("Se recibió un trap de SNMP."sudo route del -net 0.0.0.0 gw 192.168.10.1 netmask 0.0.0.0 dev virbr0)
	
    # Iteramos sobre la información obtenida.
	for name, val in varBinds: 
         # Impresión de debug.
         print(f"Debug trap: {name.prettyPrint()} : {val.prettyPrint()}")
		
         # Verificamos si está caída.
         if val.prettyPrint() == "administratively down":
            # Está caída
            estados.append(0) 

            # Guardamos la fecha actual.
            fechas_traps.append(datetime.now())

         elif val.prettyPrint() == "up":
            # Está levantada
            estados.append(1)

            # Guardamos la fecha actual.
            fechas_traps.append(datetime.now())

# Función para el hilo que captura los traps.
def funcion_hilo_traps():
    # Creamos el engine a utilizar.
    snmpEngine = engine.SnmpEngine()

    # Realizamos la configuración de transporte.
    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode(('192.168.10.10',162))
    )
    
    #Configuracion de comunidad V1 y V2c
    config.addV1System(snmpEngine, 'vista_practica', 'comunidad_practica')
	
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

@app.route('/')
def index():
    """
    Ruta principal de la aplicación que renderiza un HTML y muestra el resultado.
    """
    return render_template('index.html')

@app.route('/conteo')
def conteo():
    """
    Ruta que obtieene el conteo de paquetes en la interfaz y muestra el valor
    actual renderizado dentro de una vista HTML.
    """
    # Llamamos a la función de conteo.
    conteo = obtener_conteo()

    # Imprimimos el resultado.
    print(f"El conteo obtenido fue de: {conteo}")

    # Renderizamos el templete en HTML con la información.
    return render_template('conteo.html', conteo=conteo) 

@app.route('/conteo-grafica')
def conteo_grafica():
    """
    Ruta que genera una gráfica con la información de los conteos de paquetes
    en la interfaz de red determinada y la renderiza dentro de una vista
    HTML
    """
    # Creamos una gráfica de línea y ajustamos los labels con rotación porque las
    # fechas son largas.
    grafica = Line(x_labeL_rotation=25)

    # Colocamos las etiquetas para las fechas en X
    grafica.x_labels = map(
        lambda fecha: fecha.strftime('%H:%M:%S'), # Una lambda para formatear las fechas en hh-mm-ss
        fechas_conteos
    )

    # Añadimos nuestros conteos realizados.
    grafica.add("# de Paquetes", conteos)

    # Generamos un SVG del gráfico.
    grafica_svg = grafica.render()

    # Renderizamos un HTML dónde pasamos como argumento la gráfica.
    return render_template('conteo_grafica.html', grafica_svg=grafica_svg)


@app.route('/estado-interfaz-grafica')
def estado_interfaz_grafica():
    """
    Ruta que genera una gráfica con la información de las traps de SNMP recibidas
    con el estado de la interfaz de red.
    """
    # Creamos una gráfica de línea y ajustamos los labels con rotación porque las
    # fechas son largas.
    grafica = Line(x_labeL_rotation=25)

    # Colocamos las etiquetas para las fechas en X
    grafica.x_labels = map(
        lambda fecha: fecha.strftime('%H:%M:%S'), # Una lambda para formatear las fechas en hh-mm-ss
        fechas_traps
    )

    # Añadimos nuestros estados capturados hasta ahora.
    grafica.add("Estado de la Interfaz", estados)

    # Generamos un SVG del gráfico.
    grafica_svg = grafica.render()

    # Renderizamos un HTML dónde pasamos como argumento la gráfica.
    return render_template('estado_interfaz_grafica.html', grafica_svg=grafica_svg)

# Iniciamos el hilo para consultar la cantidad de paquetes e iniciar la escucha
# de traps.
@app.before_first_request
def iniciar_hilo_y_escucha_traps():
    # Iniciamos el hilo para consultar los paquetes.
    print("Inicializando hilos...")
    Thread(target=funcion_hilo_obtener_conteo).start()
    Thread(target=funcion_hilo_traps).start()
    print("¡Hilos inicializados correctamente!")




# Ejecutar la aplicación.
if __name__ == '__main__':
    app.run()

