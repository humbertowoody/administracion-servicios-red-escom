#/bin/bash
# Este script ejecuta el ping en python durante una hora añadiendo los resultados
# a un archivo en formato JSON.
# OJO: Debido a que el profesor no quería resultados de cada ping sino que un
#      resumen de los datos, este archivo no fue usado y se sustituyó por 3700
#      repeticiones dentro del archivo ping.py; si deseas usar este archivo 
#      primero deberás regresar ahí a 1 repetición (o lo que consideres), porque
#      de otra forma esto será eterno, o más bien solo se ejecutaría una vez.

# Calculamos la fecha de inicio.
INICIO=`date +%s`;

# Generamos el nombre del archivo a guardar.
ARCHIVO=`date +%s`.json

# Creamos un contador para fines de progreso.
CONTADOR=1

# Mensaje de incio.
echo Archivo a generar: $ARCHIVO

# Ciclo para ejecutar nuestro código durante una hora.
while [ $(( $(date +%s) - 3600 )) -lt $INICIO ];
do
  # Mensaje de confirmación para el usuario.
  echo Ejecutando ping \#$CONTADOR ...
  # Ejecutamos el script (se asume que estamos dentro del virtualenv)
  python ping.py >>$ARCHIVO; 
  # Aumentamos el contador.
  ((CONTADOR = CONTADOR + 1))
done

# Mensaje de finalización!
echo Fin de ejecución
echo Realizados $CONTADOR pings exitosos
echo Se guardaron los resultados en $ARCHIVO

# Humberto Alcocer
