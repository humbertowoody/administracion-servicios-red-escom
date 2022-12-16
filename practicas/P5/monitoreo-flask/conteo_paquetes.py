# conteo_interfaz.py 
# En este archivo definimos la función que realizará el conteo de paquetes en la interfaz de red especificada.
from pysnmp.hlapi import CommunityData, ContextData, ObjectIdentity, ObjectType, SnmpEngine, UdpTransportTarget, getCmd
from .constantes import IP_ROUTER_DEFAULT, COMUNIDAD_DEFAULT

def obtener_conteo(ip_router: str = IP_ROUTER_DEFAULT, comunidad: str = COMUNIDAD_DEFAULT) -> int:
    """
    obtener_conteo
    Función que obtiene la cantidad de paquetes que han pasado por una interfaz de red definida.
    """
    
    # Creamos un iterador a partir de un comando GET de SNMP
    iterador = getCmd(
        SnmpEngine(), # Usamos el motor de SNMP default.
        CommunityData(comunidad), # Usaremos la comunidad del argumento de la función.
        UdpTransportTarget((ip_router, 161)), # Usamos la IP del router del argumento como host de SNMP.
        ContextData(), # Creamos un contexto de datos.
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.10.1')) # Especificamos el OID del MIB que queremos obtener.
    ) 

    # Obtenemos los datos del primer resultado (podría haber más, pero solo queremos el primero).
    errorIndication, errorStatus, errorIndex, varBinds = next(iterador)

    # Validamos si hubo errores (conexión entre otros.)
    if errorIndication or errorStatus or errorIndex:
        print(f"Hubo un error contando paquetes: {errorIndication} - {errorStatus}")
        return 0 # Si, hubo un error, pero asumiremos que 0.
    else:
        # Regresamos el resultado como entero.
        return int(varBinds[0][1])



if __name__ == '__main__':
    print(f"Conteo: {obtener_conteo()} paquetes")


