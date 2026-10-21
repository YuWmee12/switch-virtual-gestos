# pylint: disable=no-member
"""
Archivo principal de ejecución
SWITCH VIRTUAL CON GESTOS DE MANO
"""
import time
import cv2
from cvzone.HandTrackingModule import HandDetector
from config import ANCHO, ALTO, CAMARA, PUERTO_SERIAL, BAUDIOS
from arduino_link import ArduinoLink
from switch_logica import Switch
from ui_drawer import dibujar, mostrar_reporte

def main():
    detector = HandDetector(detectionCon=0.6, maxHands=1)
    link = ArduinoLink(PUERTO_SERIAL, BAUDIOS)
    cap = cv2.VideoCapture(CAMARA)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)

    if not cap.isOpened():
        print("ERROR: no se pudo abrir la camara.")
        link.cerrar()
        return

    cv2.namedWindow("SWITCH VIRTUAL", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("SWITCH VIRTUAL", ANCHO, ALTO)

    sw = Switch()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            
            img = cv2.flip(cv2.resize(frame, (ANCHO, ALTO)), 1)
            
            manos, img = detector.findHands(img, draw=False)

            lm = None
            if manos:
                lm = [(pto[0], pto[1]) for pto in manos[0]["lmList"]]

            ahora = time.time()
            sw.actualizar(lm, ahora)
            link.enviar(sw.mensaje_serial())
            dibujar(img, sw, lm, ahora)
            cv2.imshow("SWITCH VIRTUAL", img)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q") or cv2.getWindowProperty("SWITCH VIRTUAL", cv2.WND_PROP_VISIBLE) < 1:
                break
            elif k == ord("r"):
                sw.reiniciar()
            elif k == ord("t"):
                sw.alternar_modo()
            elif k == ord("c"):
                sw.cancelar()
            elif k == 32: # Espacio
                sw.guardar(ahora)
    finally:
        cap.release()
        link.cerrar()
        cv2.destroyAllWindows()
        
    mostrar_reporte(sw)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
