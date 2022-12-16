# -*- coding: utf-8 -*-

import json
import pingparsing


def ping(host="8.8.8.8",repeticiones=20):
    """
    Función que recibe un host y un número de repeticiones, realiza un ping para
    cada una e imprime los datos en formato JSON.
    """
    # Creamos un objeto de PingParsing
    ping_parser=pingparsing.PingParsing()

    # Creamos un PingTransmitter
    transmitter=pingparsing.PingTransmitter()

    # Definimos el destino
    transmitter.destination=host

    # Definimos el número de repeticiones (pings) a realizar
    transmitter.count=repeticiones

    # Realizamos el ping.
    result = transmitter.ping()
    
    # Imprimimos el resultado en formato JSON.
    print(json.dumps(ping_parser.parse(result).as_dict(), indent=4))

if __name__=="__main__":
    # En la función principal llamamos a nuestra función ping.
    ping("8.8.8.8", 3700) # Como debe ser 1 hora, 3600s + 100 por si las moscas son 3700 repeticiones.
