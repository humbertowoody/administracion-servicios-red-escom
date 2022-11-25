# Monitoreo de la red de la ESCOM con un Ping

Esta tarea consiste en crear un script en Python que, usando `pingparsing`,
realice varios pings desde la red de la escuela y almacene sus resultados en
formato JSON.

## Script en Python

El script en Python (`ping.py`) define una función `ping` que cuenta con la lógica para
realizar la llamada a la función `ping` del sistema operativo y _parse_-ear
los resultados para imprimirlos en formato JSON.

Para fines de esta tarea, se define el host como `8.8.8.8` (DNS público de
Google) y usar 10 repeticiones por prueba.

## Script en Bash

Para ejecutar el ping durante una hora se generó un script en bash (`ejecutar-1-hora.sh`)
en el cual se ejecuta, durante una hora, el script en python `ping.py` y se
almacenan sus resultados en un archivo generado con el nombre de la fecha (en
formato de timestamp de UNIX) para poder procesarlo posteriormente.

## Créditos

Humberto Alejandro Ortega Alcocer
