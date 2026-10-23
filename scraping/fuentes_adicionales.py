"""Conectores de otras ligas/fuentes (federativas, competición europea...). [Solo en la versión completa]

Cada conector expone la misma interfaz que trayectoria.py: parsear_*,
scrapear_* y guardar_*, de modo que el orquestador los trata igual.
"""


def actualizar_equipo(fuente: str, equipo: str) -> None:
    raise NotImplementedError("Disponible en la versión completa.")
