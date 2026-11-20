# Taller 3 – Informática 1 (Universidad de Antioquia)

**Unidades 3 y 4: Gestión de información en computación y manejo de bases de datos.**

**Autor:** Emmanuel

Sistema modular en Python para generar, validar, ordenar, guardar y consultar registros biomédicos (signos vitales), con almacenamiento en **MongoDB Atlas**.

## Estructura del proyecto

```text
taller3-informatica1/
├── validacion.py      # Validación de registros con expresiones regulares
├── datos.py           # Generación de 50 registros aleatorios, ingreso manual y Merge Sort por FC
├── archivos.py        # TXT, CSV, JSON, carpetas /data y bitácora log.txt (os/pathlib/shutil/io)
├── mongo_db.py        # Conexión a MongoDB Atlas, inserción y consultas
├── main.py            # Menú interactivo que integra todo el sistema
├── requirements.txt   # Dependencias de Python
├── .env.example       # Plantilla de variables de entorno para MongoDB Atlas
├── .gitignore         # Archivos excluidos del control de versiones
└── README.md          # Documentación del proyecto
```

Al ejecutar el programa se crean además `data/txt/`, `data/csv/`, `data/json/` y `log.txt`.

## Formato de los registros

| Campo  | Significado                    | Formato   | Expresión regular     |
|--------|--------------------------------|-----------|-----------------------|
| `id`   | Identificación                 | `ID-001`  | `ID-\d{3}`            |
| `fr`   | Edad                           | `18 Años` | `\d{1,3} Años`        |
| `fc`   | Frecuencia cardiaca            | `090ppm`  | `\d{3}ppm`            |
| `spo2` | Saturación periférica de O₂    | `95%`     | `(?:100\|\d{2})%`     |

La validación usa `re.fullmatch`, por lo que el valor completo debe cumplir el patrón (no se aceptan espacios, saltos de línea ni texto extra).

## Funcionalidades (según la rúbrica)

1. **Procesamiento y ordenamiento (15 %)** – genera 50 registros aleatorios (`ID-001` … `ID-050`) y los ordena de menor a mayor frecuencia cardiaca con **Merge Sort** implementado a mano (compara el valor numérico, no el texto).
2. **Gestión de archivos TXT, CSV y JSON (15 %)** – guarda los datos ordenados en `.txt` y `.csv`, exporta e importa `.json`; todas las operaciones usan `try/except` y verifican la ruta (existe, es archivo, JSON válido y con lista de registros).
3. **Herramientas del sistema (10 %)** – crea `/data/txt`, `/data/csv` y `/data/json` con `pathlib`, mueve automáticamente cada archivo generado a su carpeta con `shutil` y registra cada acción con fecha y hora en `log.txt`.
4. **Expresiones regulares (10 %)** – validan `id`, `fr`, `fc` y `spo2` en el ingreso manual, al importar un JSON y antes de insertar en MongoDB. El ingreso manual también rechaza IDs repetidos.
5. **MongoDB Atlas (25 %)** – conexión con `pymongo`, colección **`signos_vitales`**, inserción solo de registros validados (sin duplicar IDs) y consultas:
   - promedio de frecuencia cardiaca,
   - documentos con SpO2 menor a 94,
   - búsqueda de un documento por `id`,
   - exportación de las dos primeras consultas a **`resultados_mongo.json`** (en `data/json/`).
6. **Integración final (15 %)** – `main.py` ofrece un menú con: ingresar datos, validar, exportar/importar archivos y conectarse a MongoDB para insertar, consultar y buscar por ID.
7. **GitHub (10 %)** – repositorio público con código, este README e historial de commits.

## Instalación y ejecución

1. Instalar dependencias (Python 3.10 o superior):
   ```bash
   pip install -r requirements.txt
   ```
2. Copiar `.env.example` como `.env` y escribir la cadena de conexión real de MongoDB Atlas en `MONGO_URI` (el archivo `.env` no se sube a GitHub):
   ```bash
   copy .env.example .env
   ```
   En Atlas, el usuario de base de datos debe tener permisos de lectura/escritura y tu IP debe estar autorizada en *Network Access*.
3. Ejecutar el sistema:
   ```bash
   python main.py
   ```

Las opciones 1 a 5 del menú funcionan sin conexión; solo las opciones 6, 7 y 8 necesitan MongoDB Atlas.

## Menú

```text
1. Generar 50 registros aleatorios y ordenar por FC
2. Ingresar un registro manual (con validación regex)
3. Validar registros en memoria
4. Exportar datos ordenados a TXT, CSV y JSON
5. Importar datos desde JSON
6. MongoDB: Insertar registros validados
7. MongoDB: Ejecutar consultas y exportar resultados_mongo.json
8. MongoDB: Consultar registro por ID
0. Salir
```

Flujo recomendado: `1` → `4` → `6` → `7` → `8`.
