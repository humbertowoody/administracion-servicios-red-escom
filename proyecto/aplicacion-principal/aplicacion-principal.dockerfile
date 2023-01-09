# Dockerfile para la aplicación principal del proyecto.
FROM arm64v8/python:3.10

# Instalamos dependencias de sistema.
RUN apt update \
	&& apt install -y \ 
	net-tools \
	iproute2 \
	iputils-ping \
	dnsutils

# Creamos el directorio de trabajo
WORKDIR /app

# Copiamos el código fuente
COPY source/requirements.txt /app/requirements.txt

# Instalamos dependencias de Python
RUN pip install -r /app/requirements.txt

# Copiamos el resto de la aplicación.
COPY source /app/

# Exponemos el puerto 5000 que usará Flask.
EXPOSE 5000 5500

# Ejecutamos la aplicación de Flask
# CMD [ "python3", "-m", "flask", "--app", "./pro.py", "run", "--host=0.0.0.0" ]
# CMD ["python3", "pro.py"]
ENTRYPOINT [ "/bin/bash" ]
