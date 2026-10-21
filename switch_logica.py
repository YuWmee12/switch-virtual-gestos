"""
Lógica principal de la máquina de estados
"""
from collections import Counter, deque
from config import SELECCION, MEDICION, GUARDADO, TIEMPO_SELECCION, TIEMPO_ESTABLE_MEDICION, TIEMPO_MOSTRAR_GUARDADO, RATIO_MIN, RATIO_MAX, SUAVIZADO, LIMITES_MB
from geometry import dist, contar_dedos, puerto_en_punto

class Switch:
    def __init__(self):
        self.modo_sel = "TOQUE"
        self.reiniciar()

    def reiniciar(self):
        self.asignado_toque = [None] * 4
        self.asignado_dedos = [None] * 4
        self._a_seleccion()
        self.mensaje = ""

    def alternar_modo(self):
        self.modo_sel = "TOQUE" if self.modo_sel == "DEDOS" else "DEDOS"
        self._a_seleccion()

    def _a_seleccion(self):
        self.estado = SELECCION
        self.puerto = 0
        self.candidato = 0
        self.t_candidato = None
        self.hist_conteo = deque(maxlen=7)
        self.conteo = 0
        self._reset_medicion()

    def _reset_medicion(self):
        self.ratio_suave = None
        self.frac = 0.0
        self.valor_mb = 0.0
        self.ref_mb = None
        self.t_estable = None

    def actualizar(self, lm, ahora):
        if self.estado == GUARDADO:
            if ahora - self.t_guardado >= TIEMPO_MOSTRAR_GUARDADO:
                self._a_seleccion()
            return

        if lm is None:
            self.hist_conteo.clear()
            self.conteo = 0
            self.candidato = 0
            self.t_candidato = None
            self.ref_mb = None
            self.t_estable = None
            return

        if self.estado == SELECCION:
            self._seleccion(lm, ahora)
        else:
            self._medicion(lm, ahora)

    def _seleccion(self, lm, ahora):
        if self.modo_sel == "DEDOS":
            self.hist_conteo.append(contar_dedos(lm))
            self.conteo = Counter(self.hist_conteo).most_common(1)[0][0]
            cand = self.conteo if 1 <= self.conteo <= 4 else 0
        else:
            cand = puerto_en_punto(*lm[8])

        if cand != self.candidato:
            self.candidato = cand
            self.t_candidato = ahora if cand else None
        elif cand and ahora - self.t_candidato >= TIEMPO_SELECCION:
            self.puerto = cand
            self.estado = MEDICION
            self.mensaje = ""
            self._reset_medicion()

    def _medicion(self, lm, ahora):
        palma = dist(lm[0], lm[9])
        if palma < 1:
            return
        ratio = dist(lm[4], lm[8]) / palma
        if self.ratio_suave is None:
            self.ratio_suave = ratio
        else:
            self.ratio_suave += SUAVIZADO * (ratio - self.ratio_suave)

        self.frac = min(1.0, max(0.0, (self.ratio_suave - RATIO_MIN) / (RATIO_MAX - RATIO_MIN)))
        limite = LIMITES_MB[self.puerto - 1]
        self.valor_mb = self.frac * limite

        tol = max(2.0, 0.08 * limite)
        if self.frac < 0.03:
            self.ref_mb, self.t_estable = None, None
        elif self.ref_mb is None or abs(self.valor_mb - self.ref_mb) > tol:
            self.ref_mb, self.t_estable = self.valor_mb, ahora
        elif ahora - self.t_estable >= TIEMPO_ESTABLE_MEDICION:
            self.guardar(ahora)

    def guardar(self, ahora):
        if self.estado != MEDICION:
            return
        limite = LIMITES_MB[self.puerto - 1]
        mb = int(round(self.valor_mb))
        
        if self.modo_sel == "TOQUE":
            self.asignado_toque[self.puerto - 1] = mb
        else:
            self.asignado_dedos[self.puerto - 1] = mb

        self.pct_guardado = int(round(100 * mb / limite)) if limite > 0 else 0
        self.mensaje = f"GUARDADO ({self.modo_sel}): PORT {self.puerto} = {mb} MB"
        self.estado = GUARDADO
        self.t_guardado = ahora

    def cancelar(self):
        if self.estado == MEDICION:
            self._a_seleccion()

    def mensaje_serial(self):
        if self.estado == SELECCION:
            return f"S{self.candidato}"
        if self.estado == MEDICION:
            return f"M{self.puerto}:{int(round(self.frac * 100))}"
        return f"G{self.puerto}:{self.pct_guardado}"
