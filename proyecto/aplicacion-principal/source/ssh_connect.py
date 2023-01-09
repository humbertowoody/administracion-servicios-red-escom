#!/usr/bin/env python3
from netmiko import ConnectHandler

"""
    @args:
        <cisco> Es el diccionario que contiene los datos para la conexion
        <cmd> Es la lista de comandos que va a ejecutar netmiko
"""
def conectar(cisco,cmd):
    net_connect = ConnectHandler(**cisco)
    net_connect.enable()
    output=[]
    for i in range(len(cmd)):
        output.append(net_connect.send_command(cmd[i]))
    return output

def conectarT(cisco,cmd):
    net_connect = ConnectHandler(**cisco)
    net_connect.enable()
    output=[]
    for i in range(len(cmd)):
        output.append(net_connect.send_config_set(cmd[i]))
    return output
    
"""
    A diferencia de la función de arriba esta puede interconectarse con
    routers con routers y no equipo a router, en forma de puente la conexión
    @args:
        <cisco> Es el diccionario que contiene los datos para la conexion
        <cmd> Es la lista de comandos que va a ejecutar netmiko
"""
def conectar_bridge(cisco,cmd):
    net_connect = ConnectHandler(**cisco)
    net_connect.enable()
    output=[]
    for i in range(len(cmd)):
        output.append(net_connect.send_command_timing(cmd[i]))
    return output
