
import time
import serial
import serial.tools.list_ports
from configuracion import INTERVALO_SERIAL

class ArduinoLink:
    def __init__(self, puerto, baudios):
        self.ser = None
        self.ultimo = None
        self.t_ultimo = 0.0
        candidatos = [puerto]
        for p in serial.tools.list_ports.comports():
            texto = f"{p.description} {p.manufacturer}".lower()
            if p.device != puerto and ("arduino" in texto or "ch340" in texto):
                candidatos.append(p.device)
        for c in candidatos:
            try:
                self.ser = serial.Serial(c, baudios, timeout=0.1)
                time.sleep(2.0)
                self.ser.reset_input_buffer()
                print(f"Arduino conectado en {c}.")
                self.enviar("X", forzar=True)
                return
            except serial.SerialException as e:
                print(f"No se pudo abrir {c}: {e}")
        print("AVISO: sin Arduino. El programa sigue funcionando solo en pantalla.")

    def enviar(self, msg, forzar=False):
        if self.ser is None or msg == self.ultimo:
            return
        ahora = time.time()
        if not forzar and msg.startswith("M") and ahora - self.t_ultimo < INTERVALO_SERIAL:
            return
        try:
            self.ser.write((msg + "\n").encode("ascii"))
            self.ultimo, self.t_ultimo = msg, ahora
        except serial.SerialException as e:
            print(f"Error serial: {e}")
            self.ser = None

    def cerrar(self):
        if self.ser is not None:
            self.enviar("X", forzar=True)
            self.ser.close()
            print("Conexion serial cerrada.")
