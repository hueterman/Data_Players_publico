"""
Utilidades comunes para los scrapers: sesión HTTP, descarga con reintentos
y parseo genérico de tablas HTML.

Respeta siempre los términos de uso y el robots.txt de cada sitio, y
mantén una espera razonable entre peticiones.
"""
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "seguimiento-jugadores-demo/0.1 (proyecto personal, uso no comercial)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "es-ES,es;q=0.9",
}


def crear_sesion() -> requests.Session:
    sesion = requests.Session()
    sesion.headers.update(DEFAULT_HEADERS)
    return sesion


def obtener_html(sesion: requests.Session, url: str, espera_seg: float = 1.0,
                 reintentos: int = 3) -> Optional[str]:
    """Descarga una URL con reintentos y espera creciente entre ellos."""
    for intento in range(1, reintentos + 1):
        try:
            respuesta = sesion.get(url, timeout=10)
            respuesta.raise_for_status()
            time.sleep(espera_seg)
            return respuesta.text
        except requests.RequestException as error:
            print(f"[intento {intento}/{reintentos}] Error al pedir {url}: {error}")
            time.sleep(espera_seg * intento)
    return None


def parsear_tabla(html: str, selector_tabla: str) -> list[dict]:
    """Convierte una tabla HTML (con fila de cabeceras) en una lista de
    diccionarios {cabecera: valor}."""
    soup = BeautifulSoup(html, "html.parser")
    tabla = soup.select_one(selector_tabla)
    if tabla is None:
        return []
    filas = tabla.find_all("tr")
    if not filas:
        return []
    cabeceras = [c.get_text(strip=True) for c in filas[0].find_all(["th", "td"])]
    datos = []
    for fila in filas[1:]:
        celdas = [c.get_text(strip=True) for c in fila.find_all("td")]
        if len(celdas) == len(cabeceras):
            datos.append(dict(zip(cabeceras, celdas)))
    return datos
