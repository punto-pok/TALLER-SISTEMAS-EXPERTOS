# -*- coding: utf-8 -*-
"""
Motor de inferencia con encadenamiento hacia adelante (forward chaining).

Componentes de un sistema experto y dónde están aquí:
  - Base de conocimiento : archivo JSON (cargar_base)
  - Memoria de trabajo   : Motor.memoria  (hecho -> paso en que se agregó)
  - Motor de inferencia  : Motor.siguiente_paso()
  - Resolución conflictos: Motor._clave()
"""
import json

# Orden de los criterios de resolución de conflictos (ver docs/documento_tecnico.md)
CRITERIOS = ["prioridad", "especificidad", "recencia", "orden en la base"]


def cargar_base(ruta):
    """Lee la base de conocimiento (JSON) y valida que sea coherente."""
    with open(ruta, encoding="utf-8") as f:
        base = json.load(f)
    catalogo = base["hechos"]
    ids = set()
    for r in base["reglas"]:
        if r["id"] in ids:
            raise ValueError(f"Regla repetida: {r['id']}")
        ids.add(r["id"])
        for h in r["antecedentes"] + r["consecuentes"]:
            if h not in catalogo:
                raise ValueError(f"Regla {r['id']}: el hecho '{h}' no está definido en 'hechos'")
    return base


def cargar_hechos(ruta):
    """Lee los hechos iniciales (JSON). Solo cuentan los que valen true."""
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    h = datos["hechos"]
    if isinstance(h, dict):          # formato {"tos": true, "fiebre": false}
        h = [k for k, v in h.items() if v]
    return datos.get("nombre", ruta), list(h)


class Motor:
    def __init__(self, base, hechos_iniciales):
        self.reglas = base["reglas"]
        self.catalogo = base["hechos"]
        for h in hechos_iniciales:
            if h not in self.catalogo:
                raise ValueError(f"Hecho desconocido: '{h}'")
        self.memoria = {h: 0 for h in hechos_iniciales}   # hecho -> paso en que entró
        self.disparadas = set()                            # refracción
        self.paso = 0

    # ---------- utilidades ----------
    def texto(self, hecho):
        return self.catalogo[hecho]["texto"]

    def _orden(self, regla):
        return self.reglas.index(regla)

    def _clave(self, r):
        """Menor clave = gana. Se usa signo negativo para ordenar de mayor a menor."""
        recencia = max(self.memoria[a] for a in r["antecedentes"])
        return (-r.get("prioridad", 0), -len(r["antecedentes"]), -recencia, self._orden(r))

    def _razon(self, conflicto):
        if len(conflicto) == 1:
            return "Es la única regla aplicable."
        a, b = self._clave(conflicto[0]), self._clave(conflicto[1])
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                va = -x if i < 3 else x + 1
                vb = -y if i < 3 else y + 1
                return f"Gana por {CRITERIOS[i]} ({va} frente a {vb})."

    # ---------- inferencia ----------
    def conflicto(self):
        """Reglas aplicables (todos sus antecedentes en memoria) y no disparadas."""
        return [r for r in self.reglas
                if r["id"] not in self.disparadas
                and set(r["antecedentes"]) <= set(self.memoria)]

    def siguiente_paso(self):
        """Ejecuta UN ciclo. Devuelve None si ya no hay reglas aplicables."""
        conflicto = self.conflicto()
        if not conflicto:
            return None
        conflicto.sort(key=self._clave)
        elegida = conflicto[0]
        self.paso += 1
        self.disparadas.add(elegida["id"])
        nuevos = [c for c in elegida["consecuentes"] if c not in self.memoria]
        for c in nuevos:
            self.memoria[c] = self.paso
        return {"paso": self.paso, "conflicto": conflicto, "elegida": elegida,
                "razon": self._razon(conflicto), "nuevos": nuevos}

    def info_regla(self, r):
        """Datos de la regla para mostrar en pantalla."""
        rec = max(self.memoria[a] for a in r["antecedentes"])
        return (f"{r['id']} {r['nombre']}  [prioridad={r.get('prioridad', 0)}, "
                f"antecedentes={len(r['antecedentes'])}, recencia={rec}]")

    # ---------- resultados ----------
    def _por_tipo(self, tipo):
        hs = [h for h in self.memoria if self.catalogo[h]["tipo"] == tipo]
        return [self.texto(h) for h in sorted(hs, key=lambda h: self.memoria[h])]

    def diagnosticos(self):
        return self._por_tipo("intermedio")

    def recomendaciones(self):
        return self._por_tipo("recomendacion")
