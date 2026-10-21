# Sistema Experto: Diagnóstico de fallas de computadores

Taller de Sistemas Expertos 2026-2S. Motor de inferencia con encadenamiento hacia adelante,
base de conocimiento en JSON (25 reglas encadenadas), resolución de conflictos propia e interfaz gráfica.

## Integrantes
Wilmer Steeven Acosta
Miguel Angel Pinilla


## Requisitos e instalación
- Python 3.8 o superior. **No hay dependencias que instalar** (`requirements.txt` solo lo documenta).
- Tkinter: viene con Python en Windows/macOS. En Linux: `sudo apt install python3-tk`.
- Clonar: `git clone <URL_DEL_REPOSITORIO>` y entrar a la carpeta.

## Ejecución
Interfaz gráfica:
```
python src/app.py
```
1. La base se carga sola; también se puede elegir otra con **Cargar base de conocimiento**.
2. Hechos iniciales: marcar síntomas a mano **o** usar **Cargar hechos desde archivo** (carpeta `casos/`).
3. **Siguiente paso** (paso a paso) o **Ejecutar todo**. La recomendación sale abajo a la derecha.

Consola (opcional):
```
python src/consola.py conocimiento/base_conocimiento.json casos/caso1_no_enciende.json
```

## Estructura de carpetas
```
sistema_experto/
├── README.md
├── requirements.txt
├── src/
│   ├── motor.py      # motor de inferencia + resolución de conflictos
│   ├── app.py        # interfaz Tkinter
│   └── consola.py    # ejecución por consola
├── conocimiento/
│   └── base_conocimiento.json   # hechos (catálogo) y 25 reglas
├── casos/            # 6 casos de ejemplo (hechos iniciales)
└── docs/
    └── documento_tecnico.md     # documento técnico (exportar a PDF)
```

## Formato de los archivos
Base de conocimiento: `hechos` (catálogo con `tipo` = sintoma | intermedio | recomendacion y `texto`)
y `reglas` (`id`, `nombre`, `antecedentes`, `consecuentes`, `prioridad` opcional).
Hechos iniciales: `{"nombre": "...", "hechos": {"tos": true, "fiebre": false}}` (solo cuentan los `true`).
