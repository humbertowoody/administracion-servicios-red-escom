# Imagen docker de un servidor DNS
FROM arm64v8/ubuntu:latest

# Dependencias de sistema
RUN apt update \
  && apt install -y \
  bind9 \
  bind9utils \
  bind9-doc \
  dnsutils \
  net-tools \
  iputils-ping \
  iproute2

# Copiamos archivos de configuración.
COPY named.conf.options /etc/bind/
COPY named.conf.local /etc/bind/
COPY db.proyecto-final.com /etc/bind/zones/

# Expose Ports
EXPOSE 53/tcp
EXPOSE 53/udp
EXPOSE 953/tcp

# Start the Name Service
CMD ["/usr/sbin/named", "-g", "-c", "/etc/bind/named.conf", "-u", "bind"]
