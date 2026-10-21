# -*- coding: utf-8 -*-
"""Interfaz gráfica simple (Tkinter) del sistema experto."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from motor import cargar_base, cargar_hechos, Motor

RAIZ = Path(__file__).resolve().parent.parent
BASE_POR_DEFECTO = RAIZ / "conocimiento" / "base_conocimiento.json"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Sistema Experto - Diagnóstico de fallas de computadores")
        root.geometry("1150x680")
        self.base = None
        self.motor = None
        self.checks = {}          # hecho -> BooleanVar

        # --- barra superior: carga de archivos ---
        top = ttk.Frame(root, padding=6)
        top.pack(fill="x")
        ttk.Button(top, text="1. Cargar base de conocimiento", command=self.pedir_base).pack(side="left")
        ttk.Button(top, text="2. Cargar hechos desde archivo", command=self.pedir_hechos).pack(side="left", padx=6)
        self.lbl = ttk.Label(top, text="Sin base cargada")
        self.lbl.pack(side="left", padx=10)

        panel = ttk.PanedWindow(root, orient="horizontal")
        panel.pack(fill="both", expand=True, padx=6, pady=6)

        # --- izquierda: hechos iniciales por interacción ---
        izq = ttk.LabelFrame(panel, text="Hechos iniciales (marque los síntomas)", padding=6)
        panel.add(izq, weight=1)
        self.lista = ttk.Frame(izq)
        self.lista.pack(fill="both", expand=True)
        botones = ttk.Frame(izq)
        botones.pack(fill="x", pady=6)
        ttk.Button(botones, text="Siguiente paso", command=self.siguiente).pack(side="left")
        ttk.Button(botones, text="Ejecutar todo", command=self.todo).pack(side="left", padx=4)
        ttk.Button(botones, text="Reiniciar", command=self.reiniciar).pack(side="left")

        # --- derecha: traza y recomendación ---
        der = ttk.Frame(panel)
        panel.add(der, weight=3)
        marco1 = ttk.LabelFrame(der, text="Inferencia paso a paso", padding=4)
        marco1.pack(fill="both", expand=True)
        self.log = tk.Text(marco1, wrap="word", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)
        marco2 = ttk.LabelFrame(der, text="RECOMENDACIÓN DEL SISTEMA", padding=4)
        marco2.pack(fill="x", pady=(6, 0))
        self.rec = tk.Text(marco2, height=9, wrap="word", font=("Segoe UI", 10, "bold"))
        self.rec.pack(fill="x")

        if BASE_POR_DEFECTO.exists():
            self.cargar_base(BASE_POR_DEFECTO)

    # ---------- carga de archivos ----------
    def pedir_base(self):
        ruta = filedialog.askopenfilename(title="Base de conocimiento", filetypes=[("JSON", "*.json")],
                                          initialdir=RAIZ / "conocimiento")
        if ruta:
            self.cargar_base(ruta)

    def cargar_base(self, ruta):
        try:
            self.base = cargar_base(ruta)
        except Exception as e:
            messagebox.showerror("Error en la base de conocimiento", str(e))
            return
        for w in self.lista.winfo_children():
            w.destroy()
        self.checks = {}
        for h, d in self.base["hechos"].items():
            if d["tipo"] == "sintoma":
                v = tk.BooleanVar()
                self.checks[h] = v
                ttk.Checkbutton(self.lista, text=d["texto"], variable=v).pack(anchor="w")
        self.lbl.config(text=f"Base: {Path(ruta).name} ({len(self.base['reglas'])} reglas)")
        self.reiniciar()

    def pedir_hechos(self):
        if not self.base:
            messagebox.showwarning("Falta la base", "Primero cargue la base de conocimiento.")
            return
        ruta = filedialog.askopenfilename(title="Hechos iniciales", filetypes=[("JSON", "*.json")],
                                          initialdir=RAIZ / "casos")
        if not ruta:
            return
        try:
            nombre, hechos = cargar_hechos(ruta)
            desconocidos = [h for h in hechos if h not in self.checks]
            if desconocidos:
                raise ValueError("Hechos que no son síntomas de la base: " + ", ".join(desconocidos))
        except Exception as e:
            messagebox.showerror("Error en el archivo de hechos", str(e))
            return
        for h, v in self.checks.items():
            v.set(h in hechos)
        self.reiniciar()
        self.escribir(f"Hechos cargados desde archivo: {nombre}\n")

    # ---------- ejecución ----------
    def escribir(self, texto):
        self.log.insert("end", texto)
        self.log.see("end")

    def iniciar(self):
        hechos = [h for h, v in self.checks.items() if v.get()]
        if not hechos:
            messagebox.showwarning("Sin hechos", "Marque al menos un síntoma o cargue un archivo.")
            return False
        self.motor = Motor(self.base, hechos)
        self.escribir("MEMORIA DE TRABAJO INICIAL:\n")
        for h in hechos:
            self.escribir(f"  + {self.motor.texto(h)}\n")
        return True

    def siguiente(self):
        if not self.base:
            return
        if self.motor is None and not self.iniciar():
            return
        p = self.motor.siguiente_paso()
        if p is None:
            self.finalizar()
            return False
        e = p["elegida"]
        self.escribir(f"\n=== PASO {p['paso']} ===\nConjunto de conflicto:\n")
        for r in p["conflicto"]:
            self.escribir(f"   - {self.motor.info_regla(r)}\n")
        self.escribir(f"Regla seleccionada: {e['id']} {e['nombre']}\nMotivo: {p['razon']}\n")
        self.escribir(f"SI {' Y '.join(e['antecedentes'])}  ENTONCES  {', '.join(e['consecuentes'])}\n")
        self.escribir(f"Hechos nuevos: {', '.join(p['nuevos']) or 'ninguno'}\n")
        return True

    def todo(self):
        while self.base and self.siguiente():
            pass

    def finalizar(self):
        self.escribir("\n=== FIN: no quedan reglas aplicables ===\n")
        self.rec.delete("1.0", "end")
        recs = self.motor.recomendaciones()
        diag = self.motor.diagnosticos()
        if diag:
            self.rec.insert("end", "Diagnóstico: " + "; ".join(diag) + "\n\n")
        if recs:
            for i, r in enumerate(recs, 1):
                self.rec.insert("end", f"{i}. {r}\n")
        else:
            self.rec.insert("end", "Sin recomendación: los datos no bastan para un diagnóstico.")

    def reiniciar(self):
        self.motor = None
        self.log.delete("1.0", "end")
        self.rec.delete("1.0", "end")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
