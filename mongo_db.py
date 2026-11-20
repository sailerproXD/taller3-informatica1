"""Conexión y consultas a MongoDB Atlas (Ítem 5)."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from archivos import exportar_json, registrar_log
from validacion import filtrar_registros_validos

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

NOMBRE_COLECCION = "signos_vitales"


def conectar_mongodb():
    """Conecta con MongoDB Atlas y retorna (cliente, colección 'signos_vitales')."""
    uri = os.getenv("MONGO_URI")
    nombre_bd = os.getenv("MONGO_DB", "bioingenieria_taller3")

    if not uri or "USUARIO:CONTRASENA" in uri:
        raise ValueError(
            "No se encontró una MONGO_URI válida. Crea un archivo .env (copia de "
            ".env.example) con tu cadena de conexión real de MongoDB Atlas."
        )

    cliente = None
    try:
        cliente = MongoClient(uri, serverSelectionTimeoutMS=8000)
        cliente.admin.command("ping")
        coleccion = cliente[nombre_bd][NOMBRE_COLECCION]
        registrar_log(
            f"Conexión exitosa a MongoDB Atlas (BD: {nombre_bd}, colección: {NOMBRE_COLECCION})."
        )
        return cliente, coleccion
    except PyMongoError as e:
        registrar_log(f"ERROR conectando a MongoDB Atlas: {e}")
        if cliente is not None:
            cliente.close()
        raise


def insertar_registros_mongo(coleccion, registros: list[dict]) -> int:
    """Valida e inserta los registros en 'signos_vitales' evitando IDs duplicados."""
    validos, invalidos = filtrar_registros_validos(registros)
    if invalidos:
        print(f"Se omitieron {len(invalidos)} registros inválidos antes de insertar.")
        registrar_log(f"{len(invalidos)} registros inválidos omitidos antes de insertar en MongoDB.")

    if not validos:
        print("No hay registros válidos para insertar.")
        return 0

    try:
        ids_existentes = set(coleccion.distinct("id"))
        nuevos: list[dict] = []
        for r in validos:
            if r["id"] in ids_existentes:
                continue
            ids_existentes.add(r["id"])  # evita duplicados dentro del mismo lote
            nuevos.append({campo: r[campo] for campo in ("id", "fr", "fc", "spo2")})

        if not nuevos:
            print("Todos los registros válidos ya existen en MongoDB.")
            return 0

        resultado = coleccion.insert_many(nuevos)
        cantidad = len(resultado.inserted_ids)
        registrar_log(
            f"Insertados {cantidad} registros validados en MongoDB ({NOMBRE_COLECCION})."
        )
        return cantidad
    except PyMongoError as e:
        print(f"Error al insertar en MongoDB: {e}")
        registrar_log(f"ERROR insertando en MongoDB: {e}")
        return 0


def consultar_promedio_fc(coleccion) -> float | None:
    """Calcula el promedio de frecuencia cardiaca (fc) con un pipeline de agregación."""
    pipeline = [
        {
            "$project": {
                "fc_num": {
                    "$toInt": {
                        "$replaceAll": {"input": "$fc", "find": "ppm", "replacement": ""}
                    }
                }
            }
        },
        {"$group": {"_id": None, "promedio_fc": {"$avg": "$fc_num"}}},
    ]

    try:
        try:
            res = list(coleccion.aggregate(pipeline))
            promedio = res[0]["promedio_fc"] if res else None
        except PyMongoError as e:
            # Respaldo: si el servidor no soporta el pipeline, se promedia en Python.
            registrar_log(f"Pipeline de promedio FC no disponible ({e}); se usa respaldo en Python.")
            valores = [
                int(d["fc"].replace("ppm", ""))
                for d in coleccion.find({}, {"_id": 0, "fc": 1})
                if isinstance(d.get("fc"), str)
            ]
            promedio = sum(valores) / len(valores) if valores else None

        if promedio is None:
            return None
        promedio = round(promedio, 2)
        registrar_log(f"Consulta MongoDB - Promedio FC: {promedio} ppm.")
        return promedio
    except (PyMongoError, ValueError) as e:
        print(f"Error calculando promedio de FC: {e}")
        registrar_log(f"ERROR en consulta promedio FC: {e}")
        return None


def consultar_spo2_menor_94(coleccion) -> list[dict]:
    """Obtiene los documentos con SpO2 menor a 94 (%)."""
    pipeline = [
        {
            "$addFields": {
                "spo2_num": {
                    "$toInt": {
                        "$replaceAll": {"input": "$spo2", "find": "%", "replacement": ""}
                    }
                }
            }
        },
        {"$match": {"spo2_num": {"$lt": 94}}},
        {"$sort": {"id": 1}},
        {"$project": {"_id": 0, "spo2_num": 0}},
    ]

    try:
        try:
            documentos = list(coleccion.aggregate(pipeline))
        except PyMongoError as e:
            registrar_log(f"Pipeline de SpO2 no disponible ({e}); se usa respaldo en Python.")
            documentos = sorted(
                (
                    d
                    for d in coleccion.find({}, {"_id": 0})
                    if isinstance(d.get("spo2"), str)
                    and int(d["spo2"].replace("%", "")) < 94
                ),
                key=lambda d: d["id"],
            )
        registrar_log(
            f"Consulta MongoDB - Documentos con SpO2 menor a 94%: {len(documentos)}."
        )
        return documentos
    except (PyMongoError, ValueError) as e:
        print(f"Error consultando SpO2 menor a 94%: {e}")
        registrar_log(f"ERROR en consulta SpO2: {e}")
        return []


def consultar_por_id(coleccion, id_buscar: str) -> dict | None:
    """Busca un documento específico en MongoDB a través del campo 'id'."""
    try:
        doc = coleccion.find_one({"id": id_buscar}, {"_id": 0})
        registrar_log(
            f"Consulta MongoDB por ID '{id_buscar}': {'encontrado' if doc else 'no encontrado'}."
        )
        return doc
    except PyMongoError as e:
        print(f"Error buscando ID '{id_buscar}': {e}")
        registrar_log(f"ERROR buscando ID '{id_buscar}': {e}")
        return None


def exportar_resultados_mongo(coleccion) -> dict:
    """Ejecuta las consultas obligatorias y las exporta a resultados_mongo.json."""
    promedio_fc = consultar_promedio_fc(coleccion)
    spo2_bajo = consultar_spo2_menor_94(coleccion)

    resultados = {
        "promedio_frecuencia_cardiaca_ppm": promedio_fc,
        "total_spo2_menor_94": len(spo2_bajo),
        "documentos_spo2_menor_94": spo2_bajo,
    }

    ruta = exportar_json(resultados, nombre="resultados_mongo.json")
    if ruta:
        print(f"Resultados de MongoDB exportados a: {ruta}")
    return resultados
