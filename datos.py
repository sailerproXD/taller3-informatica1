"""Generación, ingreso y ordenamiento de registros biomédicos (Ítem 1)."""
from __future__ import annotations

import random

from validacion import validar_registro


def generar_registros(cantidad: int = 50) -> list[dict]:
    """Genera al menos 50 registros biomédicos aleatorios con el formato del taller."""
    cantidad = max(50, cantidad)
    registros: list[dict] = []

    for i in range(1, cantidad + 1):
        registros.append(
            {
                "id": f"ID-{i:03d}",
                "fr": f"{random.randint(18, 90)} Años",
                "fc": f"{random.randint(55, 130):03d}ppm",
                "spo2": f"{random.randint(88, 100)}%",
            }
        )

    return registros


def _fc_a_entero(registro: dict) -> int:
    """Convierte '090ppm' en 90 para comparar numéricamente."""
    return int(registro["fc"].replace("ppm", ""))


def ordenar_por_fc(registros: list[dict]) -> list[dict]:
    """Ordena de menor a mayor frecuencia cardiaca usando Merge Sort (estable)."""
    if len(registros) <= 1:
        return list(registros)

    medio = len(registros) // 2
    izquierda = ordenar_por_fc(registros[:medio])
    derecha = ordenar_por_fc(registros[medio:])

    return _mezclar(izquierda, derecha)


def _mezclar(izq: list[dict], der: list[dict]) -> list[dict]:
    resultado: list[dict] = []
    i = j = 0

    while i < len(izq) and j < len(der):
        if _fc_a_entero(izq[i]) <= _fc_a_entero(der[j]):
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1

    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def ingresar_registro_manual(ids_existentes: set[str] | None = None) -> dict | None:
    """Solicita un registro por consola y lo valida con expresiones regulares.

    Rechaza el registro si algún campo no cumple el patrón o si el ID ya existe.
    """
    ids_existentes = ids_existentes or set()
    print("\n--- Ingreso manual de registro ---")
    print("Formatos -> ID: ID-051 | fr (Edad): 22 Años | fc: 085ppm | spo2: 96%")

    registro = {
        "id": input("ID: ").strip(),
        "fr": input("fr (Edad): ").strip(),
        "fc": input("fc (Frecuencia cardiaca): ").strip(),
        "spo2": input("spo2 (Saturación O2): ").strip(),
    }

    es_valido, errores = validar_registro(registro)
    if not es_valido:
        print("Registro rechazado por errores de formato:")
        for err in errores:
            print(f"  - {err}")
        return None

    if registro["id"] in ids_existentes:
        print(f"Registro rechazado: el ID '{registro['id']}' ya existe en memoria.")
        return None

    print("Registro válido.")
    return registro
