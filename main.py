"""Menú principal que integra todo el sistema (Ítem 6)."""
from __future__ import annotations

from archivos import (
    crear_estructura_carpetas,
    exportar_json,
    guardar_csv,
    guardar_txt,
    importar_json,
    registrar_log,
)
from datos import generar_registros, ingresar_registro_manual, ordenar_por_fc
from validacion import filtrar_registros_validos


def mostrar_menu() -> None:
    print("\n" + "=" * 55)
    print("   SISTEMA DE GESTIÓN DE DATOS BIOMÉDICOS - TALLER 3")
    print("=" * 55)
    print("1. Generar 50 registros aleatorios y ordenar por FC")
    print("2. Ingresar un registro manual (con validación regex)")
    print("3. Validar registros en memoria")
    print("4. Exportar datos ordenados a TXT, CSV y JSON")
    print("5. Importar datos desde JSON")
    print("6. MongoDB: Insertar registros validados")
    print("7. MongoDB: Ejecutar consultas y exportar resultados_mongo.json")
    print("8. MongoDB: Consultar registro por ID")
    print("0. Salir")
    print("=" * 55)


def opcion_mongodb(opcion: str, registros: list[dict]) -> None:
    """Ejecuta las opciones 6, 7 y 8 (todas requieren conexión a MongoDB Atlas)."""
    try:
        # Import perezoso: el resto del menú funciona aunque pymongo no esté instalado.
        from mongo_db import (
            conectar_mongodb,
            consultar_por_id,
            exportar_resultados_mongo,
            insertar_registros_mongo,
        )
    except ImportError as e:
        print(f"Falta una dependencia ({e}). Ejecuta: pip install -r requirements.txt")
        return

    cliente = None
    try:
        cliente, coleccion = conectar_mongodb()

        if opcion == "6":
            if not registros:
                print("No hay registros en memoria para subir a MongoDB.")
            else:
                n = insertar_registros_mongo(coleccion, registros)
                print(f"Registros insertados en 'signos_vitales': {n}")

        elif opcion == "7":
            resultados = exportar_resultados_mongo(coleccion)
            print(f"Promedio FC: {resultados['promedio_frecuencia_cardiaca_ppm']} ppm")
            print(f"Documentos con SpO2 menor a 94: {resultados['total_spo2_menor_94']}")

        elif opcion == "8":
            id_buscar = input("Ingresa el ID a consultar (ej. ID-001): ").strip().upper()
            doc = consultar_por_id(coleccion, id_buscar)
            if doc:
                print("Documento encontrado:", doc)
            else:
                print(f"No se encontró ningún registro con ID '{id_buscar}'.")

    except Exception as e:  # sin conexión, credenciales inválidas, .env ausente...
        print(f"Error en operación de MongoDB: {e}")
    finally:
        if cliente is not None:
            cliente.close()


def main() -> None:
    try:
        crear_estructura_carpetas()
    except OSError as e:
        print(f"No se pudo crear la estructura de carpetas: {e}")
        return

    registros: list[dict] = []
    registrar_log("Inicio de sesión en main.py.")

    while True:
        mostrar_menu()
        try:
            opcion = input("Selecciona una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            opcion = "0"

        if opcion == "1":
            registros = ordenar_por_fc(generar_registros(50))
            registrar_log("Generados y ordenados 50 registros biomédicos aleatorios.")
            print(f"Se generaron y ordenaron {len(registros)} registros por FC.")
            print("Primeros 3 registros:", registros[:3])

        elif opcion == "2":
            nuevo = ingresar_registro_manual({r["id"] for r in registros})
            if nuevo:
                registros.append(nuevo)
                registros = ordenar_por_fc(registros)
                registrar_log(f"Registro manual agregado: {nuevo['id']}.")
                print(f"Registro {nuevo['id']} agregado y lista reordenada.")

        elif opcion == "3":
            if not registros:
                print("No hay registros en memoria. Genera o importa datos primero.")
                continue
            validos, invalidos = filtrar_registros_validos(registros)
            registrar_log(
                f"Validación ejecutada: {len(validos)} válidos, {len(invalidos)} inválidos."
            )
            print(f"Válidos: {len(validos)} | Inválidos: {len(invalidos)}")
            for item in invalidos:
                print("  Inválido:", item["registro"], "->", item["errores"])

        elif opcion == "4":
            if not registros:
                print("No hay registros en memoria para exportar.")
                continue
            ordenados = ordenar_por_fc(registros)
            print(f"TXT guardado en:  {guardar_txt(ordenados)}")
            print(f"CSV guardado en:  {guardar_csv(ordenados)}")
            print(f"JSON guardado en: {exportar_json(ordenados)}")

        elif opcion == "5":
            ruta = input(
                "Ruta del JSON (Enter para usar data/json/registros_ordenados.json): "
            ).strip()
            importados = importar_json(ruta if ruta else None)
            if importados:
                # Los datos importados también se validan con las expresiones regulares.
                validos, invalidos = filtrar_registros_validos(importados)
                registrar_log(
                    f"Importación validada: {len(validos)} válidos, {len(invalidos)} descartados."
                )
                if invalidos:
                    print(f"Se descartaron {len(invalidos)} registros inválidos:")
                    for item in invalidos:
                        print("  Inválido:", item["registro"], "->", item["errores"])
                if validos:
                    registros = ordenar_por_fc(validos)
                    print(f"Se cargaron {len(registros)} registros válidos en memoria.")
                else:
                    print("Ningún registro del archivo es válido; no se cargó nada.")

        elif opcion in {"6", "7", "8"}:
            opcion_mongodb(opcion, registros)

        elif opcion == "0":
            registrar_log("Cierre del sistema.")
            print("Saliendo del programa.")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
