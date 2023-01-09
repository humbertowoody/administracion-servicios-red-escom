# Script para construir todas las imágenes Docker necesarias.

# Mensaje de inicio.
echo "Construyendo imágenes de Docker...";

# Aplicación Principal
docker build -t aplicacion-principal:latest ./aplicacion-principal/ -f ./aplicacion-principal/aplicacion-principal.dockerfile && echo "Aplicación principal lista!";

# Servidor Web
docker build -t servidor-web:latest ./servidor-web/ -f ./servidor-web/servidor-web.dockerfile && echo "Servidor HTTP listo!";

# Servidor DNS
docker build -t servidor-dns:latest ./servidor-dns/ -f ./servidor-dns/servidor-dns.dockerfile && echo "Servidor DNS listo!";

# Fin.
echo "Fin de construcción de imágenes Docker";

