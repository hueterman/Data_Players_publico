"""
Scraper de ejemplo: trayectoria (equipos por los que ha pasado un jugador).

Es el único scraper completo de la versión pública. La página de origen
muestra el historial como texto repetido "AAAA - AAAA" seguido del nombre
del equipo, así que el patrón se busca por texto en lugar de por selector
CSS (más robusto a cambios de clases). Se prueba contra un fixture local:
ver tests/test_trayectoria.py.

Define la URL de la fuente en la variable de entorno TRAYECTORIA_URL_BASE
(plantilla con {slug}), p. ej.  https://ejemplo.com/jugadores/{slug}/trayectoria
Antes de apuntar a un sitio real, revisa sus términos de uso.
"""
import os
import re
from typing import Optional

from bs4 import BeautifulSoup

from db.conexion import get_connection, obtener_o_crear_equipo
from scraping.base_scraper import crear_sesion, obtener_html

PATRON_TEMPORADA = re.compile(r"^(\d{4})\s*-\s*(\d{4})$")


def _siguiente_texto_no_vacio(nodo) -> Optional[str]:
    for siguiente in nodo.find_all_next(string=True):
        texto = siguiente.strip()
        if texto:
            return texto
    return None


def parsear_trayectoria(html: str) -> list[dict]:
    """Lista de {temporada, equipo}, una por etapa, en el orden de la página."""
    soup = BeautifulSoup(html, "html.parser")
    nodos = [n for n in soup.find_all(string=True) if PATRON_TEMPORADA.match(n.strip())]
    etapas = []
    for nodo in nodos:
        equipo = _siguiente_texto_no_vacio(nodo)
        if equipo:
            etapas.append({"temporada": nodo.strip().replace(" ", ""), "equipo": equipo})
    return etapas


def scrapear_trayectoria(slug_jugador: str) -> list[dict]:
    plantilla = os.environ.get("TRAYECTORIA_URL_BASE")
    if not plantilla:
        raise RuntimeError("Define TRAYECTORIA_URL_BASE (plantilla con {slug}).")
    html = obtener_html(crear_sesion(), plantilla.format(slug=slug_jugador))
    return parsear_trayectoria(html) if html else []


def guardar_trayectoria(jugador_id: int, etapa: dict, competicion: str = "Liga Demo") -> None:
    """Inserta o actualiza una etapa. Idempotente gracias al índice único
    (jugador_id, equipo_id, temporada)."""
    equipo_id = obtener_o_crear_equipo(etapa["equipo"], competicion=competicion)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO trayectoria (jugador_id, equipo_id, temporada)
            VALUES (?, ?, ?)
            ON CONFLICT(jugador_id, equipo_id, temporada) DO NOTHING;
            """,
            (jugador_id, equipo_id, etapa["temporada"]),
        )
