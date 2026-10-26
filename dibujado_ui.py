import cv2
import numpy as np
from configuracion import FUENTE, SELECCION, MEDICION, GUARDADO, LIMITES_MB, TIEMPO_SELECCION, TIEMPO_ESTABLE_MEDICION, ANCHO, ALTO, BOX_W, BOX_H, BOX_GAP, BOX_X0, BOX_Y
from geometria import rect_puerto, dist, boton_menu_en_punto

def texto_ui(img, s, org, escala=0.8, color=(255, 255, 255), grosor=2, centrado=False):
    if centrado:
        (w, h), _ = cv2.getTextSize(s, FUENTE, escala, grosor)
        org = (org[0] - w // 2, org[1])
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
        activo = (sw.estado == SELECCION and sw.candidato == n) or \
                 (sw.estado != SELECCION and sw.puerto == n)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255) if activo else (0, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        
        col = (0, 0, 0) if activo else (0, 255, 255)
        
        texto_ui(img, f"limite {LIMITES_MB[i]} MB", (x1 + 10, y1 + 30), 0.7, col, 2)
        if sw.asignado_toque[i] is not None or sw.asignado_dedos[i] is not None:
            val_t = f"T:{sw.asignado_toque[i]}M" if sw.asignado_toque[i] is not None else ""
            val_d = f"D:{sw.asignado_dedos[i]}M" if sw.asignado_dedos[i] is not None else ""
            texto_ui(img, f"{val_t} {val_d}", (x1 + 10, y1 + 65), 0.7, (0, 255, 0), 2)
        texto_ui(img, f"PUERTO {n}", (x1 + 10, y2 - 10), 0.9, col, 2)

    ancho_total = 4 * BOX_W + 3 * BOX_GAP
    x0, y0 = BOX_X0, BOX_Y + BOX_H + 30

    if lm is None and sw.estado != GUARDADO:
        texto_ui(img, "Mano no detectada", (x0, y0 + 30), 1.2, (0, 0, 255), 3)

    if sw.estado == SELECCION:
        extra = f" | Dedos: {sw.conteo}" if sw.modo_sel == "DEDOS" else ""
        texto_ui(img, f"SELECCION - modo {sw.modo_sel}{extra}", (x0, y0 + 10), 1.0, (0, 255, 255), 3)
        
        if sw.candidato:
            falta = max(0.0, TIEMPO_SELECCION - (ahora - sw.t_candidato))
            texto_ui(img, f"PUERTO {sw.candidato}: manten {falta:.1f}s o pellizca", (x0, y0 + 50), 1.1, (0, 255, 0), 3)
            barra(img, x0, y0 + 70, x0 + ancho_total, y0 + 90, (ahora - sw.t_candidato) / TIEMPO_SELECCION, (0, 255, 0))
            
        if sw.modo_sel == "TOQUE" and lm is not None:
            palma = dist(lm[0], lm[9])
            ratio = dist(lm[4], lm[8]) / palma if palma > 10 else 1.0
            col_cursor = (0, 255, 0) if ratio < 0.15 else (255, 0, 255)
            p1, p2 = (int(lm[4][0]), int(lm[4][1])), (int(lm[8][0]), int(lm[8][1]))
            cv2.line(img, p1, p2, col_cursor, 3)
            cv2.circle(img, p1, 8, col_cursor, cv2.FILLED)
            cv2.circle(img, p2, 8, col_cursor, cv2.FILLED)

    elif sw.estado == MEDICION:
        limite = LIMITES_MB[sw.puerto - 1]
        texto_ui(img, f"MEDICION - PUERTO {sw.puerto}", (x0, y0 + 10), 0.9, (0, 255, 255), 3)
        if lm is not None:
            p1 = (int(lm[4][0]), int(lm[4][1]))
            p2 = (int(lm[8][0]), int(lm[8][1]))
            cv2.line(img, p1, p2, (255, 0, 255), 4)
            cv2.circle(img, p1, 10, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, p2, 10, (255, 255, 0), cv2.FILLED)
            
        texto_ui(img, f"{int(round(sw.valor_mb))} MB", (ANCHO // 2, ALTO // 2 + 30), 3.0, (0, 255, 255), 5, centrado=True)
        
        if sw.t_estable is not None:
            prog = (ahora - sw.t_estable) / TIEMPO_ESTABLE_MEDICION
            texto_ui(img, f"Estable: guardando en {max(0.0, TIEMPO_ESTABLE_MEDICION - (ahora - sw.t_estable)):.1f}s", (x0, y0 + 50), 1.0, (0, 255, 0), 3)
            barra(img, x0, y0 + 70, x0 + ancho_total, y0 + 90, prog, (0, 255, 0))
        
        rx1, rx2, ry1, ry2 = BOX_X0, BOX_X0 + ancho_total, ALTO - 100, ALTO - 60
        barra(img, rx1, ry1, rx2, ry2, sw.frac, (0, 200, 0))
        texto_ui(img, "0 MB", (rx1, ry1 - 15), 0.8)
        texto_ui(img, f"LIMITE: {limite} MB", (rx2 - 180, ry1 - 15), 0.8)

    else:
        texto_ui(img, sw.mensaje, (x0, y0 + 40), 1.4, (0, 255, 0), 4)

    # --- PANELES LATERALES (2 IZQUIERDA / 3 DERECHA, LIBERANDO LA BARRA) ---
    overlay = img.copy()
    
    # Coordenadas verticales de los botones
    y_izq = [ALTO - 260, ALTO - 170] # [Q] SALIR, [R] REINICIAR
    y_der = [ALTO - 350, ALTO - 260, ALTO - 170] # [T] MODO, [ESP] GUARDAR, [C] CANCELAR
    h_btn = 75
    
    # Dibujar izquierda (2 botones)
    for y_b in y_izq:
        cv2.rectangle(overlay, (20, y_b), (170, y_b + h_btn), (25, 25, 25), cv2.FILLED)
        cv2.rectangle(overlay, (20, y_b), (170, y_b + h_btn), (100, 100, 100), 1)
        
    # Dibujar derecha (3 botones)
    for y_b in y_der:
        cv2.rectangle(overlay, (ANCHO - 170, y_b), (ANCHO - 20, y_b + h_btn), (25, 25, 25), cv2.FILLED)
        cv2.rectangle(overlay, (ANCHO - 170, y_b), (ANCHO - 20, y_b + h_btn), (100, 100, 100), 1)

    btn_hover = boton_menu_en_punto(*lm[8]) if lm is not None else -1
    if btn_hover != -1:
        if btn_hover in [0, 1]:
            cv2.rectangle(overlay, (20, y_izq[btn_hover]), (170, y_izq[btn_hover] + h_btn), (80, 80, 80), cv2.FILLED)
        elif btn_hover in [2, 3, 4]:
            idx_der = btn_hover - 2
            cv2.rectangle(overlay, (ANCHO - 170, y_der[idx_der]), (ANCHO - 20, y_der[idx_der] + h_btn), (80, 80, 80), cv2.FILLED)

    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    # Textos Izquierda
    texto_ui(img, "[Q] SALIR", (95, y_izq[0] + 45), 0.55, (255, 255, 255), 1, centrado=True)
    texto_ui(img, "[R] REINICIAR", (95, y_izq[1] + 45), 0.5, (255, 255, 255), 1, centrado=True)
    
    # Textos Derecha
    texto_ui(img, "[T] MODO", (ANCHO - 95, y_der[0] + 45), 0.55, (255, 255, 255), 1, centrado=True)
    texto_ui(img, "[ESP] GUARDAR", (ANCHO - 95, y_der[1] + 45), 0.48, (255, 255, 255), 1, centrado=True)
    texto_ui(img, "[C] CANCELAR", (ANCHO - 95, y_der[2] + 45), 0.5, (255, 255, 255), 1, centrado=True)

def mostrar_reporte(sw):
    # Ventana adaptada a las mismas dimensiones exactas de la pantalla principal (1000x620)
    ancho_rep, alto_rep = 1000, 620
    img = np.zeros((alto_rep, ancho_rep, 3), dtype=np.uint8)
    img[:] = (20, 20, 20) # Fondo oscuro moderno
    
    # Encabezado superior estilizado
    cv2.rectangle(img, (0, 0), (ancho_rep, 75), (35, 35, 35), cv2.FILLED)
    cv2.line(img, (0, 75), (ancho_rep, 75), (60, 60, 60), 2)
    texto_ui(img, "REPORTE FINAL - CONFIGURACION MULTISESION", (50, 47), 0.95, (255, 255, 255), 2)
    
    def dibujar_tarjeta_horizontal(y_offset, titulo, datos, color_tema):
        # Tarjeta contenedora principal (ocupa casi todo el ancho de la pantalla)
        cv2.rectangle(img, (40, y_offset), (ancho_rep - 40, y_offset + 225), (30, 30, 30), cv2.FILLED)
        cv2.rectangle(img, (40, y_offset), (ancho_rep - 40, y_offset + 225), (70, 70, 70), 2)
        
        # Título de la sesión dentro de la tarjeta
        cv2.putText(img, titulo, (65, y_offset + 35), FUENTE, 0.75, color_tema, 2, cv2.LINE_AA)
        cv2.line(img, (65, y_offset + 50), (ancho_rep - 65, y_offset + 50), (60, 60, 60), 1)
        
        # Distribuir los 4 puertos en 2 columnas dentro de la tarjeta para aprovechar el espacio a lo ancho
        for i in range(4):
            val = datos[i]
            lim = LIMITES_MB[i]
            
            # Columna 1 (Puertos 1 y 2) o Columna 2 (Puertos 3 y 4)
            columna = i // 2
            fila = i % 2
            
            x_base = 75 if columna == 0 else 535
            y_row = y_offset + 95 + (fila * 60)
            
            cv2.putText(img, f"PUERTO {i+1}:", (x_base, y_row), FUENTE, 0.65, (200, 200, 200), 1, cv2.LINE_AA)
            
            if val is not None:
                cv2.putText(img, f"{val} / {lim} MB", (x_base + 115, y_row), FUENTE, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Barra gráfica proporcional más ancha y elegante
                bar_x = x_base + 235
                bar_w = 140
                fill_w = int((val / lim) * bar_w) if lim > 0 else 0
                cv2.rectangle(img, (bar_x, y_row - 14), (bar_x + bar_w, y_row + 4), (50, 50, 50), cv2.FILLED)
                cv2.rectangle(img, (bar_x, y_row - 14), (bar_x + fill_w, y_row + 4), color_tema, cv2.FILLED)
            else:
                cv2.putText(img, "Sin lectura", (x_base + 115, y_row), FUENTE, 0.65, (120, 120, 120), 1, cv2.LINE_AA)
                bar_x = x_base + 235
                bar_w = 140
                cv2.rectangle(img, (bar_x, y_row - 14), (bar_x + bar_w, y_row + 4), (40, 40, 40), cv2.FILLED)

    # Dibujar las dos tarjetas distribuidas verticalmente
    dibujar_tarjeta_horizontal(95, "SESION TOQUE", sw.asignado_toque, (0, 255, 255))
    dibujar_tarjeta_horizontal(335, "SESION DEDOS", sw.asignado_dedos, (255, 128, 0))
    
    # Pie de página indicativo
    cv2.putText(img, "Presiona cualquier tecla para cerrar el sistema...", (45, 595), FUENTE, 0.55, (150, 150, 150), 1, cv2.LINE_AA)
    
    cv2.namedWindow("REPORTE FINAL", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("REPORTE FINAL", ancho_rep, alto_rep)
    cv2.imshow("REPORTE FINAL", img)
    cv2.waitKey(0)