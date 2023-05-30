from netmiko import ConnectHandler

def crear_usuario(host, usuario):
  # Preparamos los datos de conexión ssh.
  cisco = {
    "device_type": "cisco_xe",
    "ip": host["ip"], 
    "username": "admin", 
    "password": "admin01",
    "secret": "12345678" 
  }
  
  # Nos conectamos.
  conexion = ConnectHandler(**cisco)

  conexion.enable()

  comandos = [
    f'username {usuario["nombre"]} privilege 15 password {usuario["pass"]}',
  ]

  conexion.send_config_set(comandos)

  conexion.disconnect()

  return {'estado': 'exito', 'nombre': usuario["nombre"], 'contraseña': usuario['pass']}