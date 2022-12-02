#!/bin/python
# Ejemplo de Animación con Matplotlib y PingParsing.
# Este es un programa muy simple que genera una animación de los resultados de 
# pings realizados a un host particular usando Matplotlib.
#
# Electroadictos - Administración de Servicios en Red - 4CM11
# ESCOM IPN
# 30 Noviembre 2022

# Importamos datetime para obtener las fechas de cada ejecución de ping.
import datetime as dt

# Importamos matplotlib de forma general para colocar configuraciones (línea 10)
import matplotlib as mpl

# Importamos la clase de animación.
import matplotlib.animation as animation

# Importamos pyplot.
import matplotlib.pyplot as plt

# Importamos pingparsing para las operaciones con ping.
import pingparsing

# Desactivamos el toolbar de Matplotlib.
# Nota: Se deja comentado porque en MacOS se rompe si lo desactivamos, viva Apple.
# mpl.rcParams['toolbar'] = 'None'

# Modo oscuro, como Batman.
plt.style.use('dark_background')


# Clase para hacer pings.
class Pinger:
    TIMEOUT = 10 # Timeout por defecto de cada ping, en segundos.

    def __init__(self, host: str, timeout: int = TIMEOUT):
        """
        El constructor de la clase solo instancía el parser y el transmitter,
        así como definir la configuración del transmitter para nuestro caso de
        uso.
        """
        self.host = host
        self.parser = pingparsing.PingParsing()
        self.transmitter = pingparsing.PingTransmitter()
        self.transmitter.destination = host
        self.transmitter.count = 1
        self.transmitter.timeout = timeout

    def ping_rtt_avg(self) -> float:
        """
        Función que llamaremos para realizar el "ping" y obtener su round-trip-time
        promedio (tiempo de viaje redondo).
        """
        try:
            resp = self.transmitter.ping(); # Hacemos el ping.
            result = self.parser.parse(resp).as_dict() # Obtenemos los resultados como diccionario.
            rtt = float(result["rtt_avg"]) # Obtenemos, del diccionario, el dato que nos interesa.
        except Exception:
            rtt = self.TIMEOUT # En caso de cualquier excepción, regresamos el timeout.

        return rtt


# Clase para Graficar dinámicamente los Pings recibidos.
class GraficadorPing:
    LIMITE = 10  # Límite de pings a mostrar por defecto.
    INTERVALO = 500 # Intervalo de actualización de gráfica (en ms) por defecto.

    def __init__(self, pinger: Pinger, limite: int = LIMITE, intervalo: int = INTERVALO):
        """
        Constructor de la clase con el que inicializamos nuestro Pinger, arreglos
        para los datos y nuestro "plot".
        """
        # Pinger
        self.pinger = pinger

        # Límite de pings e intervalo de actualización de gráfica.
        self.limite = limite
        self.intervalo = intervalo

        # Data para los ejes.
        self.timestamps = []
        self.rtts = []

        # Iniciamos el subplot para la gráfica.
        self.fig, self.ax = plt.subplots()

    def __actualizar_data(self):
        """
        Función que actualizará la data en cada llamada. Es decir, agregará
        un rtt_avg de cada ping y la fecha actual.
        """
        rtt = self.pinger.ping_rtt_avg() # Hacemos el ping.

        # Imprimimos mensaje con la información obtenida.
        print(f"Se obtuvo un ping de: {rtt}ms a {self.pinger.host}")

        # Agregamos la fecha actual a nuestro arreglo de fechas.
        self.timestamps.append(dt.datetime.now())

        # Ajustamos arreglo para que solo tenga self.limite elementos.
        self.timestamps = self.timestamps[-self.limite:]

        # Agregamos el rtt_avg obtenido del ping.
        self.rtts.append(rtt)

        # Ajustamos arreglo para que solo tenga self.limite elementos.
        self.rtts = self.rtts[-self.limite:]

    def __renderizar_frame(self, i: int):
        """
        Función que será llamada por Matplotlib para renderizar cada frame en 
        el intervalo de tiempo definido en self.intervalo.
        """
        # Llamamos a la función miembro que actualiza la información.
        self.__actualizar_data()

        
        # Limpiamos los ejes.
        self.ax.clear()

        # Colocamos las opciones para la cuadrícula
        #  - Activada
        #  - De tipo línea (--)
        #  - Con un ancho de 0.25px 
        self.ax.grid(True, ls='--', lw=0.25)

        # Especificamos que la gráfica será de tipo "fecha" y ajustamos configuración.
        #  - Primer argumento arreglo con las fechas.
        #  - Segundo argumento arreglo con los rtt_avg
        #  - Tipo de línea sólida
        #  - Tipo de ajuste entre puntos por "pasos", es decir, trazarlo como tren de pulsos (saludos a mi profa de señales :D)
        #  - Marcadores para cada punto: None.
        self.ax.plot_date(self.timestamps, self.rtts, ds='steps', fmt='-')

        # Colocamos título a la gráfica y al eje Y.
        host = self.pinger.host
        plt.title('Latencia de ping a {}'.format(host))
        plt.ylabel('Tiempo de respuesta (ms)')

    def iniciar(self):
        """
        Función que se llamará para iniciar la animación.
        """

        # Llamamos a la función de Matplotlib para dejar conectada a nuestra
        # función de animación.
        #  - La figura de Matplotlib que deberá usarse.
        #  - La función que queremos que se llame cada cierto intervalo.
        #  - El intervalo de tiempo (en ms) que queremos que actualice la data.
        # Nota: usen una variable para que Python pueda limpiar la memoria eficazmente y su gráfica no se trabe.
        a = animation.FuncAnimation(
            fig=self.fig,
            func=self.__renderizar_frame,
            interval=self.intervalo,
        )

        # Mostramos la gráfica!
        plt.show()


if __name__ == "__main__":
    """
    Función principal.
    """
    # Creamos un pinger a 8.8.8.8 con 1s de timeout.
    pinger = Pinger("8.8.8.8", timeout=1)

    # Creamos nuestro graficador de pings con un límite de 50 pings y un intervalo de 500ms.
    plotter = GraficadorPing(pinger, limite=50, intervalo=500)

    # Iniciamos la graficación.
    plotter.iniciar()

