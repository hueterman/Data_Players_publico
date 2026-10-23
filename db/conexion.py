"""
Acceso a la base de datos y helpers de catálogos/equipos, compartidos por
los scrapers y por la interfaz de formularios.

Versión pública: incluye lo necesario para que la app y el scraper de
ejemplo funcionen. La lógica de reconciliación de jugadores entre fuentes
(alias, identificadores externos, fusión de duplicados) no se publica.
"""
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DB_PATH

CATALOGOS_VALIDOS = {
    "posiciones", "tipos_movimiento", "manos_dominantes", "estados_jugador",
    "fuentes", "niveles_fiabilidad", "grados_gravedad", "estados_lesion",
    "tipos_contrato",
}


@contextmanager
def get_connection():
    """Abre una conexión con claves foráneas activadas; commit/rollback automático."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _validar_catalogo(nombre_tabla: str) -> None:
    if nombre_tabla not in CATALOGOS_VALIDOS:
        raise ValueError(f"'{nombre_tabla}' no es un catálogo reconocido.")


def listar_catalogo(nombre_tabla: str) -> list[sqlite3.Row]:
    """Devuelve todas las filas (id, nombre) de una tabla de catálogo."""
    _validar_catalogo(nombre_tabla)
    with get_connection() as conn:
        return conn.execute(f"SELECT id, nombre FROM {nombre_tabla} ORDER BY id;").fetchall()


def id_por_nombre(nombre_tabla: str, nombre_valor: str) -> int | None:
    """Id de un valor de catálogo por su nombre (ej. 'Activo' en estados_jugador)."""
    _validar_catalogo(nombre_tabla)
    with get_connection() as conn:
        fila = conn.execute(
            f"SELECT id FROM {nombre_tabla} WHERE nombre = ?;", (nombre_valor,)
        ).fetchone()
        return fila["id"] if fila else None


def buscar_o_crear_jugador(nombre: str, apellidos: str) -> tuple[int, bool]:
    """Devuelve (jugador_id, creado). Búsqueda simple por nombre+apellidos
    sin distinguir mayúsculas. (La versión completa reconcilia además
    variantes de nombre entre fuentes.)"""
    with get_connection() as conn:
        fila = conn.execute(
            "SELECT id FROM jugadores WHERE nombre = ? COLLATE NOCASE "
            "AND apellidos = ? COLLATE NOCASE;",
            (nombre, apellidos),
        ).fetchone()
        if fila:
            return fila["id"], False
        cursor = conn.execute(
            "INSERT INTO jugadores (nombre, apellidos) VALUES (?, ?);", (nombre, apellidos)
        )
        return cursor.lastrowid, True


def obtener_o_crear_equipo(nombre: str, competicion: str | None = None,
                           nivel: str | None = None, pais: str | None = None) -> int:
    """Busca un equipo por nombre (y competición si se indica); si no existe, lo crea."""
    with get_connection() as conn:
        if competicion:
            fila = conn.execute(
                "SELECT id FROM equipos WHERE nombre = ? AND competicion = ?;",
                (nombre, competicion),
            ).fetchone()
        else:
            fila = conn.execute("SELECT id FROM equipos WHERE nombre = ?;", (nombre,)).fetchone()
        if fila:
            return fila["id"]
        cursor = conn.execute(
            "INSERT INTO equipos (nombre, competicion, nivel, pais) VALUES (?, ?, ?, ?);",
            (nombre, competicion, nivel, pais),
        )
        return cursor.lastrowid
