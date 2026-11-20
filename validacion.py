"""Validación de registros biomédicos con expresiones regulares (Ítem 4)."""
from __future__ import annotations

import re

# Patrones definidos en el apartado 1 del taller:
#   id   -> "ID-001"
#   fr   -> "18 Años"   (edad)
#   fc   -> "090ppm"    (frecuencia cardiaca, siempre 3 dígitos)
#   spo2 -> "95%"       (0 a 100)
PATRONES = {
    "id": r"ID-\d{3}",
    "fr": r"\d{1,3} Años",
    "fc": r"\d{3}ppm",
    "spo2": r"(?:100|\d{2})%",
}

_PATRONES_COMPILADOS = {campo: re.compile(p) for campo, p in PATRONES.items()}


def validar_campo(campo: str, valor) -> bool:
    """Indica si el valor cumple EXACTAMENTE el patrón del campo (fullmatch)."""
    patron = _PATRONES_COMPILADOS.get(campo)
    return patron is not None and isinstance(valor, str) and patron.fullmatch(valor) is not None


def validar_registro(registro: dict) -> tuple[bool, list[str]]:
    """Valida los cuatro campos (id, fr, fc, spo2) de un registro con regex."""
    if not isinstance(registro, dict):
        return False, ["El registro no es un diccionario válido."]

    errores: list[str] = []
    for campo, patron in PATRONES.items():
        valor = registro.get(campo)
        if not validar_campo(campo, valor):
            errores.append(
                f"Campo '{campo}' inválido ('{valor}'). Patrón esperado: {patron}"
            )

    return len(errores) == 0, errores


def filtrar_registros_validos(
    registros: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Separa los registros válidos de los inválidos (con sus errores)."""
    validos: list[dict] = []
    invalidos: list[dict] = []

    for reg in registros:
        es_valido, errores = validar_registro(reg)
        if es_valido:
            validos.append(reg)
        else:
            invalidos.append({"registro": reg, "errores": errores})

    return validos, invalidos
