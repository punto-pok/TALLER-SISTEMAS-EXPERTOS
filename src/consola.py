# -*- coding: utf-8 -*-
"""Ejecución por consola (útil para probar sin interfaz).
Uso: python src/consola.py conocimiento/base_conocimiento.json casos/caso1_no_enciende.json
"""
import sys
from motor import cargar_base, cargar_hechos, Motor

base = cargar_base(sys.argv[1])
nombre, hechos = cargar_hechos(sys.argv[2])
m = Motor(base, hechos)
print("=== " + nombre + " ===")
print("Memoria de trabajo inicial:", ", ".join(hechos))
while (p := m.siguiente_paso()) is not None:
    print(f"\n--- Paso {p['paso']} ---")
    print("Conflicto:", " | ".join(r["id"] for r in p["conflicto"]))
    print("Elegida  :", m.info_regla(p["elegida"]))
    print("Motivo   :", p["razon"])
    print("Nuevos   :", ", ".join(p["nuevos"]) or "ninguno")
print("\nDIAGNÓSTICO:", *m.diagnosticos(), sep="\n  - ")
print("\nRECOMENDACIONES:", *(m.recomendaciones() or ["Sin recomendación: datos insuficientes."]), sep="\n  - ")
