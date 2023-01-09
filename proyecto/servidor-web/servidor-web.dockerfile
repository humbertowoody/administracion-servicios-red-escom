# Imagen Docker de un servidor web simple usando nginx y una página sencilla.
FROM arm64v8/nginx:latest

# Dependencias de sistema.
RUN apt update \
  && apt install -y \
  net-tools \
  iproute2 \
  iputils-ping \
  dnsutils

# Copiamos nuestro index.html al servidor.
COPY index.html /usr/share/nginx/html