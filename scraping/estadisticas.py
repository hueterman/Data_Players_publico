"""Scraper de estadísticas por temporada y de carrera. [Solo en la versión completa]

Interfaz pública (la implementación no se incluye):
- scrapear_estadisticas(slug) -> list[dict]   # una fila por temporada
- guardar_estadisticas(jugador_id, filas)     # idempotente
"""


def scrapear_estadisticas(slug_jugador: str) -> list[dict]:
    raise NotImplementedError("Disponible en la versión completa.")


def guardar_estadisticas(jugador_id: int, filas: list[dict]) -> None:
    raise NotImplementedError("Disponible en la versión completa.")
