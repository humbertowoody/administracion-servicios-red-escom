# Demo - Generación de Gráficas usando Flask

Este demo permite visualizar cómo sería tener una ruta en Flask que realice
una serie de `ping`s a cierto `host` con cierto `timeout` y se retorne la
imagen de Flask.

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
pip 22.3.1 from /Users/humbertowoody/Proyectos/IPN/administracion-de-servicios-en-red/demo-flask-matplotlib/demo-flask-matplotlib/venv/lib/python3.10/site-packages/pip (python 3.10)
```

Y ¡listo! ahora estamos listos para ejecutar el programa.

## Rutas disponibles

Para este demo sólamente generamos dos rutas principales.

1. `GET /grafica`: Ruta básica que genera una gráfica simple y la muestra como imagen.
2. `GET /ping/:host?cantidad=x&timeout=y`: Ruta que realiza `cantidad` `x` de pings
   al `:host` con un `timeout` máximo de `y` segundos y muestra su gráfica.

Si deseas consultar la definición de las rutas que _son visibles_ para Flask, puedes
utilizar el siguiente comando:

```sh
$ flask routes
```

Lo cual nos regresará una salida similar a:

```txt
Endpoint        Methods  Rule
--------------  -------  -----------------------
grafica_simple  GET      /grafica
ping_host       GET      /ping/<host>
static          GET      /static/<path:filename>
```

## Ejecución

Para realizar la ejecución del programa, bastará con usar el comando:

```sh
$ flask run --host=0.0.0.0
```

> Nota: usamos el `--host=0.0.0.0` para que nuestro servidor de Flask escuche
> en todas las interfaces de red disponibles.

La salida será algo similar a:

```sh
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.100.67.116:5000
Press CTRL+C to quit
```

## Visualización de gráficas.

Dado que el programa genera las imágenes dentro de una etiqueta HTML con la imagen
generada en Base64, lo más simple será usar cualquier navegador web para
poder visualizar la información.

Así se vería la llamada a `/grafica`:

![Imagen de Gráfica Base][grafica-1]

Así se vería la llamada a `/ping/8.8.8.8` (sin argumentos extra):

![Imagen de Gráfica a Ping sin Argumentos][grafica-2]

Así se vería la llamada a `/ping/8.8.8.8?timeout=10&cantidad=100`:

![Imagen de Gráfica de Ping con Argumentos][grafica-3]

> Recomendamos el uso de [Postman][link-postman] para hacer pruebas de APIs ya
> que simplifica _muchísimo_ el proceso de debug y configuración.

## Créditos

Este programa fue realizado por:

- Equipo: Electroadictos.
- Materia: Administración de Servicios en Red.
- Grupo: 4CM11
- Profesor: Ricardo Martínez Rosales.
- Semestre: 23/1

[grafica-1]: docs/grafica-1.png
[grafica-2]: docs/grafica-2.png
[grafica-3]: docs/grafica-3.png
[link-postman]: https://www.postman.com/downloads/
