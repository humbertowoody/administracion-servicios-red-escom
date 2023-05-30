# conteo_interfaz.py 
# En este archivo definimos la función que realizará el conteo de paquetes en la interfaz de red especificada.
from pysnmp.hlapi import CommunityData, ContextData, ObjectIdentity, ObjectType, SnmpEngine, UdpTransportTarget, getCmd, setCmd, OctetString
from constantes import IP_ROUTER_DEFAULT, COMUNIDAD_DEFAULT

OID_DEFAULT = '1.3.6.1.2.1.2.2.1.10.1'

def obtener_valor_oid(ip_router: str = IP_ROUTER_DEFAULT, comunidad: str = COMUNIDAD_DEFAULT, oid: str = OID_DEFAULT) -> any:
    """
    obtener_valor_oid
    Función que obtiene la cantidad de paquetes que han pasado por una interfaz de red definida.
    """
    
    # Creamos un iterador a partir de un comando GET de SNMP
    iterador = getCmd(
        SnmpEngine(), # Usamos el motor de SNMP default.
        CommunityData(comunidad), # Usaremos la comunidad del argumento de la función.
        UdpTransportTarget((ip_router, 161)), # Usamos la IP del router del argumento como host de SNMP.
        ContextData(), # Creamos un contexto de datos.
        ObjectType(ObjectIdentity(oid)) # Especificamos el OID del MIB que queremos obtener.
    )


    # Obtenemos los datos del primer resultado (podría haber más, pero solo queremos el primero).
    errorIndication, errorStatus, errorIndex, varBinds = next(iterador)

    # Validamos si hubo errores (conexión entre otros.)
    if errorIndication or errorStatus or errorIndex:
        print(f"Hubo un error obteniendo el valor: {errorIndication} - {errorStatus}")
        return 0 # Si, hubo un error, pero asumiremos que 0.
    else:
        # Regresamos el resultado como entero.
        return varBinds[0][1]

def colocar_valor_oid(ip_router: str = IP_ROUTER_DEFAULT, comunidad: str = COMUNIDAD_DEFAULT, oid: str ='1.3.6.1.2.1.1.1', valor: str = 'Desripción Default') -> bool:

    # Creamos un iterador a partir de un comando GET de SNMP
    iterador = setCmd(
        SnmpEngine(), # Usamos el motor de SNMP default.
        CommunityData(comunidad), # Usaremos la comunidad del argumento de la función.
        UdpTransportTarget((ip_router, 161)), # Usamos la IP del router del argumento como host de SNMP.
        ContextData(), # Creamos un contexto de datos.
        ObjectType(ObjectIdentity(oid), OctetString(valor)) # Especificamos el OID del MIB que queremos obtener.
    )

    # Obtenemos los datos del primer resultado (podría haber más, pero solo queremos el primero).
    errorIndication, errorStatus, errorIndex, varBinds = next(iterador)

    # Validamos si hubo errores (conexión entre otros.)
    if errorIndication or errorStatus or errorIndex:
        print(f"Hubo un error en comando SET de SNMP ({oid}): {errorIndication} - {errorStatus}")
        return False
    else:
        # Regresamos un True
        return True

def oid_paquetes_entrantes_interfaz(id_interfaz: int = 1) -> str:
    return f'1.3.6.1.2.1.2.2.1.10.{id_interfaz}'

def oid_paquetes_salientes_interfaz(id_interfaz: int = 1) -> str:
    return f'1.3.6.1.2.1.2.2.1.16.{id_interfaz}'

def oid_paquetes_erroneos_interfaz(id_interfaz: int = 1) -> str:
    return f'1.3.6.1.2.1.2.2.1.20.{id_interfaz}'

def oid_para_uptime() -> str:
    return '.1.3.6.1.2.1.1.3.0'

def oid_para_ip_interfaces() -> str:
    return '.1.3.6.1.2.1.4.20.1.1'

def oid_para_hostname() -> str:
    return '1.3.6.1.4.1.9.2.1.3.0'

def oid_para_syscontact() -> str:
    return '1.3.6.1.2.1.1.4.0'

def oid_para_syslocation() -> str:
    return '1.3.6.1.2.1.1.6.0'

def oid_para_sysdescription() -> str:
    return '1.3.6.1.2.1.1.1.0'


if __name__ == '__main__':
    print(f'Datos SNMP para {IP_ROUTER_DEFAULT} comunidad {COMUNIDAD_DEFAULT}')
    print(f'Uptime - {obtener_valor_oid(oid=oid_para_uptime())}')
    print(f'Hostname - {obtener_valor_oid(oid=oid_para_hostname())}')
    print(f'SysContact - {obtener_valor_oid(oid=oid_para_syscontact())}')
    print(f'SysLocation - {obtener_valor_oid(oid=oid_para_syslocation())}')
    print(f'SysDescription - {obtener_valor_oid(oid=oid_para_sysdescription())}')
    print('Interfaces:')
    for i in range(1,6):
        print(f'\t- Interfaz #{i}:')
        print(f"\t\t- Paquetes entrantes: {obtener_valor_oid(oid=oid_paquetes_entrantes_interfaz(i))} paquetes")
        print(f"\t\t- Paquetes salientes: {obtener_valor_oid(oid=oid_paquetes_salientes_interfaz(i))} paquetes")
        print(f"\t\t- Paquetes erroneos: {obtener_valor_oid(oid=oid_paquetes_erroneos_interfaz(i))} paquetes")
