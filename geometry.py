"""
Funciones matemáticas y geométricas
"""
import math
from config import BOX_X0, BOX_W, BOX_GAP, BOX_Y, BOX_H, UMBRAL_POLEGAR

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def rect_puerto(i):
    x1 = BOX_X0 + i * (BOX_W + BOX_GAP)
    return x1, BOX_Y, x1 + BOX_W, BOX_Y + BOX_H

def puerto_en_punto(x, y):
    for i in range(4):
        x1, y1, x2, y2 = rect_puerto(i)
        if x1 <= x <= x2 and y1 <= y <= y2:
            return i + 1
    return 0

def contar_dedos(lm):
    if lm is None or len(lm) < 21:
        return 0
    n = 0
    if dist(lm[4], lm[17]) > dist(lm[3], lm[17]) * UMBRAL_POLEGAR:
        n += 1
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        if dist(lm[0], lm[tip]) > dist(lm[0], lm[pip]) * 1.05:
            n += 1
    return n
