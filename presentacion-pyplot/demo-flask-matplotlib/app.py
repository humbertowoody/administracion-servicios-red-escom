#!/bin/python
# Ejemplo de generación de gráfica con datos a través de Flask.
# Este es un programa muy simple que genera una gráfica simple en un endpoint
# así cómo otra ruta que permite realizar N número de pings a un host particular
# con cierto timeout y genera su gráfica correspondiente.
#
# Electroadictos - Administración de Servicios en Red - 4CM11
# ESCOM IPN
# 30 Noviembre 2022

# Importamos Flask y request para obtener información relacionada a cada
# request relacionada.
from flask import Flask, request

# Importamos Matplotlib.
import matplotlib

# Elegimos usar el renderizador "Agg" que no requiere usar el entorno gráfico
# de nuestro Sistema Operativo.
matplotlib.use('Agg')

# Importamos Pyplot.
import matplotlib.pyplot as plt

# Importamos el paquete de manejo de entrada y salida.
import io

# Importamos el paquete para uso de codificación Base 64.
import base64

# Importamos pingparsing
import pingparsing

# Importamos el paquete de control de fechas.
import datetime as dt

# Definimos la aplicación principal de Flask.
app = Flask(__name__)

@app.route('/ping/<host>')
def ping_host(host: str = "8.8.8.8"):
    """
    /ping/:host
    Ruta que realiza 10 pings al valor de `host` y retorna su gráfica generada por
    Matplotlib
    """
    # Obtenemos los argumentos opcionales para configurar el request.
    cantidad_pings = request.args.get("cantidad", default = 10, type=int)
    timeout = request.args.get("timeout", default = 1, type=int)

    # Generamos el parser.
    parser = pingparsing.PingParsing()

    # Generamos el transmitter.
    transmitter = pingparsing.PingTransmitter()

    # Ajustamos configuración del transmitter.
    transmitter.destination = host # Host como argumento de la función.
    transmitter.count = 1 # Cantidad de pings a realizar por llamada.
    transmitter.timeout = timeout  # Timeout máximo de cada ping.

    # Nuestros arreglos con la información obtenida.
    timestamps = []
    rtts = []

    # Mostramos un mensaje de confirmación.
    print(f"Se realizarán {cantidad_pings} pings a {host} con un timeout de {timeout}s")

    # Realizamos los 10 pings en un ciclo for.
    for i in range(0, cantidad_pings):
        # Realizamos el ping.
        respuesta = transmitter.ping()

        # Extraemos nuestra respuesta como diccionario.
        resultado = parser.parse(respuesta).as_dict()

        # Agregamos nuestro resultado al arreglo.
        rtts.append(resultado["rtt_avg"])

        # Agregamos nuestra fecha actual a nuestro arreglo.
        timestamps.append(dt.datetime.now())

        # Mostramos mensaje en la consola.
        print(f"- Ping #{i} a {host} {resultado['rtt_avg']}ms")

    # Generamos la gráfica.
    plt.plot(timestamps, rtts)

    # Colocamos configuración de Matplotlib.
    plt.grid()

    # Colocamos título a la gráfica y el eje Y.
    plt.title(f'{cantidad_pings} pings a {host} con timeout de {timeout}s')
    plt.ylabel('Tiempo de respuesta (ms)')

    # Creamos el contenedor de la imagen de tipo BytesIO.
    img = io.BytesIO()

    # Guardamos la imagen en formato PNG dentro de nuestro contenedor de imagen.
    plt.savefig(img, format='png')

    # Regresamos el cursor del contenedor al inicio.
    img.seek(0)

    # Generamos la cadena en Base64 con la imagen.
    grafica_base64 = base64.b64encode(img.getvalue()).decode()

    # Limpiamos la gráfica.
    plt.clf()

    # Regresamos la imagen en formato Base64
    return '<img src="data:image/png;base64,{}">'.format(grafica_base64)

@app.route('/grafica')
def grafica_simple():
    """
    /grafica
    Función que genera una gráfica simple y la retorna como una cadena Base64 
    en formato imagen.
    """
    # Generamos el contenedor para la imagen de tipo BytesIO.
    img = io.BytesIO()

    # Datos para la gráfica.
    y = [1,2,3,4,5]
    x = [0,2,1,3,4]

    # Generamos la gráfica.
    plt.plot(x,y)

    # Guardamos la gráfica en formato PNG dentro de nuestro contenedor.
    plt.savefig(img, format='png')

    # Regresamos el cursor de la imagen al inicio del contenedor.
    img.seek(0)

    # Generamos la cadena en Base64 que usaremos para la imagen.
    cadena_base64 = base64.b64encode(img.getvalue()).decode()

    # Limpiamos la gráfica.
    plt.clf()

    # Retornamos la imagen.
    return '<img src="data:image/png;base64,{}">'.format(cadena_base64)

if __name__ == '__main__':
    """
    Función principal.
    """
    # Activamos el modo de debug.
    app.debug = True

    # Ejecutamos la aplicación.
    app.run()
