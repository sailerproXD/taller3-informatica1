"""Gestión de archivos TXT/CSV/JSON y herramientas del sistema (Ítems 2 y 3)."""
from __future__ import annotations

import csv
import io
import json
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RUTAS = {
    "txt": DATA_DIR / "txt",
    "csv": DATA_DIR / "csv",
    "json": DATA_DIR / "json",
}
LOG_FILE = BASE_DIR / "log.txt"
CAMPOS = ["id", "fr", "fc", "spo2"]


def registrar_log(accion: str) -> None:
    """Registra una acción con fecha y hora en log.txt."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, mode="a", encoding="utf-8") as f:
            f.write(f"[{marca_tiempo}] {accion}\n")
    except OSError as e:
        print(f"Error al escribir en log.txt: {e}")


def crear_estructura_carpetas() -> dict[str, Path]:
    """Crea la estructura /data/txt, /data/csv y /data/json si no existe."""
    try:
        for ruta in RUTAS.values():
            ruta.mkdir(parents=True, exist_ok=True)
        registrar_log(
            "Estructura de carpetas verificada/creada (/data/txt, /data/csv, /data/json)."
        )
    except OSError as e:
        registrar_log(f"ERROR creando carpetas: {e}")
        raise
    return RUTAS


def mover_a_carpeta(archivo_origen: Path, tipo: str) -> Path:
    """Mueve automáticamente un archivo generado a su subcarpeta en /data."""
    if tipo not in RUTAS:
        raise ValueError(f"Tipo de archivo no soportado: {tipo}")

    if not archivo_origen.is_file():
        raise FileNotFoundError(f"No existe el archivo a mover: {archivo_origen}")

    crear_estructura_carpetas()
    destino = RUTAS[tipo] / archivo_origen.name
    shutil.move(str(archivo_origen), str(destino))
    registrar_log(
        f"Archivo '{archivo_origen.name}' movido automáticamente a '{destino.relative_to(BASE_DIR)}'."
    )
    return destino


def guardar_txt(
    registros: list[dict], nombre: str = "registros_ordenados.txt"
) -> Path | None:
    """Guarda los registros ordenados en formato TXT (columnas alineadas)."""
    try:
        buffer = io.StringIO()
        buffer.write(f"{'ID':<10}{'Edad (fr)':<14}{'FC':<10}{'SpO2':<6}\n")
        buffer.write("-" * 40 + "\n")
        for r in registros:
            buffer.write(f"{r['id']:<10}{r['fr']:<14}{r['fc']:<10}{r['spo2']:<6}\n")

        temp_path = BASE_DIR / nombre
        with open(temp_path, mode="w", encoding="utf-8") as f:
            f.write(buffer.getvalue())
        buffer.close()

        destino = mover_a_carpeta(temp_path, "txt")
        registrar_log(
            f"Exportados {len(registros)} registros a TXT en '{destino.relative_to(BASE_DIR)}'."
        )
        return destino
    except (OSError, KeyError, ValueError) as e:
        print(f"Error al guardar TXT: {e}")
        registrar_log(f"ERROR al guardar TXT: {e}")
        return None


def guardar_csv(
    registros: list[dict], nombre: str = "registros_ordenados.csv"
) -> Path | None:
    """Guarda los registros ordenados en CSV y los organiza en /data/csv."""
    if not registros:
        print("No hay registros para guardar en CSV.")
        return None

    try:
        temp_path = BASE_DIR / nombre
        # utf-8-sig: Excel muestra correctamente la "ñ" de "Años".
        with open(temp_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(registros)

        destino = mover_a_carpeta(temp_path, "csv")
        registrar_log(
            f"Exportados {len(registros)} registros a CSV en '{destino.relative_to(BASE_DIR)}'."
        )
        return destino
    except (OSError, KeyError, ValueError) as e:
        print(f"Error al guardar CSV: {e}")
        registrar_log(f"ERROR al guardar CSV: {e}")
        return None


def exportar_json(datos, nombre: str = "registros_ordenados.json") -> Path | None:
    """Exporta datos en formato JSON y los organiza en /data/json."""
    temp_path = BASE_DIR / nombre
    try:
        with open(temp_path, mode="w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

        destino = mover_a_carpeta(temp_path, "json")
        registrar_log(f"Datos exportados a JSON en '{destino.relative_to(BASE_DIR)}'.")
        return destino
    except (OSError, TypeError, ValueError) as e:
        print(f"Error al exportar JSON: {e}")
        registrar_log(f"ERROR al exportar JSON: {e}")
        # Si falló a medias, no dejar un JSON corrupto suelto en la raíz.
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        return None


def importar_json(ruta_archivo: str | None = None) -> list[dict]:
    """Importa registros desde un archivo JSON verificando la ruta."""
    ruta = (
        Path(ruta_archivo.strip().strip('"'))
        if ruta_archivo
        else (RUTAS["json"] / "registros_ordenados.json")
    )

    try:
        if not ruta.exists():
            raise FileNotFoundError(f"La ruta '{ruta}' no existe.")
        if not ruta.is_file():
            raise ValueError(f"La ruta '{ruta}' no es un archivo.")

        with open(ruta, mode="r", encoding="utf-8-sig") as f:
            datos = json.load(f)

        if not isinstance(datos, list):
            raise ValueError("El archivo JSON no contiene una lista de registros.")

        registrar_log(f"Importados {len(datos)} registros desde '{ruta}'.")
        return datos
    except (OSError, ValueError) as e:  # incluye FileNotFoundError y JSONDecodeError
        print(f"Error al importar JSON: {e}")
        registrar_log(f"ERROR al importar JSON desde '{ruta}': {e}")
        return []
