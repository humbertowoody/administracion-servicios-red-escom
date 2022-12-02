# Demo 1 - Animación de Ping en Python usando Matplotlib

Este simple ejemplo es una aplicación que, usando Matplotlib, realiza `ping`s
a un host particular y los grafica dinámicamente, es decir, de forma animada.

Un ejemplo de cómo se ve la salida es el siguiente GIF:

![Demo de Animación][demo-ping-gif]

## Instalación

Para instalar el programa, lo primero será crear un ambiente virtual:

```sh
python3 -m venv ./venv
```

Luego, _activaremos_ dicho ambiente virtual:

```sh
source ./venv/bin/activate
```

> **Ojo**: dependiendo de tu intérprete de terminal (Bash, ZSH, Fish, etc.) puede
> ser que este comando debas modificarlo para no afectar tu ambiente.

Una vez activado, siempre es bueno verificar las versiones de Python y PIP que
tenemos instaladas, en mi caso, son las siguientes:

```sh
$ python --version && pip --version
Python 3.10.8
pip 22.3.1 from /Users/humbertowoody/Proyectos/IPN/administracion-de-servicios-en-red/demo-presentacion/animacion/venv/lib/python3.10/site-packages/pip (python 3.10)
```

Y ¡listo! ahora estamos listos para ejecutar el programa.

## Ejecución

Para ejecutar el programa asegúrate de haber seguido los pasos de [instalación](#Instalación)
que están mas arriba. Para ejecutar, bastará con usar:

```sh
python graficador-ping.py
```

Y deberías comenzar a ver en la terminal los siguientes logs:

```txt
Se obtuvo un ping de: 10.574ms a 8.8.8.8
Se obtuvo un ping de: 8.054ms a 8.8.8.8
Se obtuvo un ping de: 5.759ms a 8.8.8.8
Se obtuvo un ping de: 7.113ms a 8.8.8.8
Se obtuvo un ping de: 6.17ms a 8.8.8.8
Se obtuvo un ping de: 8.713ms a 8.8.8.8
Se obtuvo un ping de: 6.01ms a 8.8.8.8
```

Y en tu ambiente gráfico la siguiente animación:

## Parámetros y configuraciones

Existen diversos parámetros y configuraciones que podemos modificar del programa
para ajustarlo a lo que requerimos.

### Pinger

En el caso del pinger, podemos cambiar:

- `timeout`: Se refiere al tiempo _máximo_ que esperaremos para la respuesta de
  nuestro paquete ICMP (es decir, el `ping`).
- `count`: La cantidad de `ping`s que realizaremos, para este ejmplo el _ideal_ es 1, pero puedes probar con otros valores y comparar tus resultados.
- `host`: El destino de nuestro `ping`, está definido a `8.8.8.8` que es el DNS público de Google y normalmente no falla, pero prueba con otros destinos para ver información más útil.

### Graficador

En el caso del graficador, podemos modificar los siguientes parámetros:

- `limite`: El límite de datos a mostrar en la gráfica, es decir, el número máximo de `ping`s que queremos visualizar en la animación.
- `intervalo`: El intervalo de actualización de la gráfica, en milisgundos.

Internamente en el código puedes buscar las opciones de Matplotlib específicamente para realizar cambios.

## Créditos

Este programa fue realizado por:

- Equipo: Electroadictos.
- Materia: Administración de Servicios en Red.
- Grupo: 4CM11
- Profesor: Ricardo Martínez Rosales.
- Semestre: 23/1

[demo-ping-gif]: docs/demo-animacion-ping.gif
