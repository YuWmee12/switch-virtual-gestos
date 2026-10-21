"""
Gráficos y dibujo de la interfaz de usuario
"""
import cv2
import numpy as np
from config import FUENTE, SELECCION, MEDICION, GUARDADO, LIMITES_MB, TIEMPO_SELECCION, TIEMPO_ESTABLE_MEDICION, ANCHO, ALTO, BOX_W, BOX_H, BOX_GAP, BOX_X0, BOX_Y
from geometry import rect_puerto

def texto_ui(img, s, org, escala=0.8, color=(255, 255, 255), grosor=2):
    cv2.putText(img, s, org, FUENTE, escala, (0, 0, 0), grosor + 2, cv2.LINE_AA)
    cv2.putText(img, s, org, FUENTE, escala, color, grosor, cv2.LINE_AA)

def barra(img, x1, y1, x2, y2, frac, color):
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
    ancho = int((x2 - x1) * min(1.0, max(0.0, frac)))
    if ancho > 0:
        cv2.rectangle(img, (x1, y1), (x1 + ancho, y2), color, -1)

def dibujar(img, sw, lm, ahora):
    for i in range(4):
        n = i + 1
        x1, y1, x2, y2 = rect_puerto(i)
        activo = (sw.estado == SELECCION and sw.candidato == n) or                  (sw.estado != SELECCION and sw.puerto == n)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255) if activo else (0, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        
        col = (0, 0, 0) if activo else (0, 255, 255)
        
        texto_ui(img, f"limite {LIMITES_MB[i]} MB", (x1 + 10, y1 + 30), 0.7, col, 2)
        if sw.asignado_toque[i] is not None or sw.asignado_dedos[i] is not None:
            val_t = f"T:{sw.asignado_toque[i]}M" if sw.asignado_toque[i] is not None else ""
            val_d = f"D:{sw.asignado_dedos[i]}M" if sw.asignado_dedos[i] is not None else ""
            texto_ui(img, f"{val_t} {val_d}", (x1 + 10, y1 + 65), 0.7, (0, 255, 0), 2)
        texto_ui(img, f"PORT {n}", (x1 + 10, y2 - 10), 0.9, col, 2)

    ancho_total = 4 * BOX_W + 3 * BOX_GAP
    x0, y0 = BOX_X0, BOX_Y + BOX_H + 30

    if lm is None and sw.estado != GUARDADO:
        texto_ui(img, "No se detecta mano", (x0, y0 + 30), 1.2, (0, 0, 255), 3)

    if sw.estado == SELECCION:
        extra = f" | Dedos: {sw.conteo}" if sw.modo_sel == "DEDOS" else ""
        texto_ui(img, f"SELECCION - modo {sw.modo_sel}{extra}", (x0, y0 + 10), 1.0, (0, 255, 255), 3)
        
        if sw.candidato:
            falta = max(0.0, TIEMPO_SELECCION - (ahora - sw.t_candidato))
            texto_ui(img, f"PORT {sw.candidato}: manten {falta:.1f}s", (x0, y0 + 50), 1.1, (0, 255, 0), 3)
            barra(img, x0, y0 + 70, x0 + ancho_total, y0 + 90, (ahora - sw.t_candidato) / TIEMPO_SELECCION, (0, 255, 0))
            
        if sw.modo_sel == "TOQUE" and lm is not None:
            cv2.circle(img, (int(lm[8][0]), int(lm[8][1])), 15, (255, 0, 255), cv2.FILLED)

    elif sw.estado == MEDICION:
        limite = LIMITES_MB[sw.puerto - 1]
        texto_ui(img, f"MEDICION - PORT {sw.puerto} (ESPACIO para guardar)", (x0, y0 + 10), 0.9, (0, 255, 255), 3)
        if lm is not None:
            p1 = (int(lm[4][0]), int(lm[4][1]))
            p2 = (int(lm[8][0]), int(lm[8][1]))
            cv2.line(img, p1, p2, (255, 0, 255), 4)
            cv2.circle(img, p1, 10, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, p2, 10, (255, 255, 0), cv2.FILLED)
            
        texto_ui(img, f"{int(round(sw.valor_mb))} MB", (ANCHO // 2 - 120, ALTO // 2 + 30), 3.0, (0, 255, 255), 5)
        
        if sw.t_estable is not None:
            prog = (ahora - sw.t_estable) / TIEMPO_ESTABLE_MEDICION
            texto_ui(img, f"Estable: guardando en {max(0.0, TIEMPO_ESTABLE_MEDICION - (ahora - sw.t_estable)):.1f}s", (x0, y0 + 50), 1.0, (0, 255, 0), 3)
            barra(img, x0, y0 + 70, x0 + ancho_total, y0 + 90, prog, (0, 255, 0))
        else:
            texto_ui(img, "Abre/cierra dedos o presiona ESPACIO para guardar", (x0, y0 + 50), 0.9, (255, 255, 255), 2)
        
        rx1, rx2, ry1, ry2 = BOX_X0, BOX_X0 + ancho_total, ALTO - 90, ALTO - 50
        barra(img, rx1, ry1, rx2, ry2, sw.frac, (0, 200, 0))
        texto_ui(img, "0 MB", (rx1, ry1 - 15), 0.8)
        texto_ui(img, f"LIMITE: {limite} MB", (rx2 - 250, ry1 - 15), 0.8)

    else:
        texto_ui(img, sw.mensaje, (x0, y0 + 40), 1.4, (0, 255, 0), 4)

    # --- NUEVO MENÚ INFERIOR MEJORADO ---
    alto_img, ancho_img = img.shape[:2]
    
    # 1. Crear un fondo oscuro semitransparente en la parte inferior
    overlay = img.copy()
    cv2.rectangle(overlay, (0, alto_img - 45), (ancho_img, alto_img), (15, 15, 15), cv2.FILLED)
    # Línea decorativa superior del menú
    cv2.line(overlay, (0, alto_img - 45), (ancho_img, alto_img - 45), (200, 100, 0), 2)
    cv2.addWeighted(overlay, 0.85, img, 0.15, 0, img)
    
    # 2. Lista de botones y acciones
    opciones = [
        ("Q", "Salir"), 
        ("R", "Reiniciar"), 
        ("T", "Modo"), 
        ("ESPACIO", "Guardar"), 
        ("C", "Cancelar")
    ]
    
    x_offset = 20
    y_text = alto_img - 15
    
    # 3. Dibujar cada opción de forma estilizada
    for tecla, accion in opciones:
        # Dibujar la tecla en corchetes y color Amarillo/Cyan
        tecla_str = f"[{tecla}]"
        (w_t, _), _ = cv2.getTextSize(tecla_str, FUENTE, 0.65, 2)
        cv2.putText(img, tecla_str, (x_offset, y_text), FUENTE, 0.65, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, tecla_str, (x_offset, y_text), FUENTE, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
        x_offset += w_t + 8
        
        # Dibujar la descripción de la acción en color blanco
        (w_a, _), _ = cv2.getTextSize(accion, FUENTE, 0.65, 1)
        cv2.putText(img, accion, (x_offset, y_text), FUENTE, 0.65, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(img, accion, (x_offset, y_text), FUENTE, 0.65, (240, 240, 240), 1, cv2.LINE_AA)
        
        # Espaciado para el siguiente botón
        x_offset += w_a + 35
    # ------------------------------------

def mostrar_reporte(sw):
    img = np.zeros((700, 950, 3), dtype=np.uint8)
    cv2.putText(img, "--- CONFIGURACION FINAL ---", (40, 45), FUENTE, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # 1. Sección Sesión Toque
    cv2.putText(img, "SESION TOQUE:", (40, 95), FUENTE, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    for i in range(4):
        v = sw.asignado_toque[i]
        val_str = f"{v} MB" if v is not None else "sin lectura"
        col = (0, 255, 0) if v is not None else (120, 120, 120)
        linea = f"  PORT {i + 1}: {val_str}   (limite {LIMITES_MB[i]} MB)"
        cv2.putText(img, linea, (40, 130 + i * 35), FUENTE, 0.65, col, 2, cv2.LINE_AA)
        
    # 2. Sección Sesión Dedos
    cv2.putText(img, "SESION DEDOS:", (40, 305), FUENTE, 0.8, (255, 128, 0), 2, cv2.LINE_AA)
    for i in range(4):
        v = sw.asignado_dedos[i]
        val_str = f"{v} MB" if v is not None else "sin lectura"
        col = (0, 255, 0) if v is not None else (120, 120, 120)
        linea = f"  PORT {i + 1}: {val_str}   (limite {LIMITES_MB[i]} MB)"
        cv2.putText(img, linea, (40, 340 + i * 35), FUENTE, 0.65, col, 2, cv2.LINE_AA)
        
    cv2.putText(img, "Presiona cualquier tecla para cerrar", (40, 635), FUENTE, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.imshow("REPORTE FINAL", img)
    cv2.waitKey(0)
