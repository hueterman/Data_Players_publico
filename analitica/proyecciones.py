"""
Proyección de PIR (valoración) para la temporada siguiente: línea base.

Versión pública: media ponderada de las dos últimas temporadas (más peso a
la reciente y a quien juega más partidos) con un ajuste simple por edad.
Sirve como referencia ("baseline") contra la que medir modelos mejores.

El modelo completo (features por 100 posesiones normalizadas por liga,
validación walk-forward y comparación de varios regresores) no forma parte
de la versión pública.

    python -m analitica.proyecciones
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DB_PATH

# Ajuste de PIR por tramo de edad (curva de envejecimiento muy simplificada)
AJUSTE_EDAD = [(0, 21, +1.0), (21, 24, +0.5), (24, 30, 0.0), (30, 33, -0.5), (33, 99, -1.5)]


def _ajuste_por_edad(edad: float) -> float:
    for minimo, maximo, ajuste in AJUSTE_EDAD:
        if minimo <= edad < maximo:
            return ajuste
    return 0.0


def generar_proyecciones(conn: sqlite3.Connection) -> pd.DataFrame:
    stats = pd.read_sql_query(
        """
        SELECT et.jugador_id, et.temporada, et.partidos_jugados, et.valoracion_pir
        FROM estadisticas_temporada et
        WHERE et.valoracion_pir IS NOT NULL AND et.partidos_jugados > 0;
        """,
        conn,
    )
    if stats.empty:
        raise ValueError("No hay estadísticas con valoración PIR en la base de datos.")

    ultimas = stats.sort_values("temporada").groupby("jugador_id").tail(2)
    ultimas = ultimas.assign(peso=ultimas["partidos_jugados"] * (1 + (ultimas["temporada"] == ultimas.groupby("jugador_id")["temporada"].transform("max"))))
    agregado = ultimas.groupby("jugador_id").apply(
        lambda g: pd.Series({
            "pir_base": (g["valoracion_pir"] * g["peso"]).sum() / g["peso"].sum(),
            "temporada": g["temporada"].max(),
            "pir_origen": g.sort_values("temporada")["valoracion_pir"].iloc[-1],
        }),
        include_groups=False,
    ).reset_index()

    jugadores = pd.read_sql_query(
        """
        SELECT j.id AS jugador_id, j.nombre, j.apellidos, j.fecha_nacimiento, j.foto_url,
               p.nombre AS posicion,
               (SELECT eq.nombre FROM trayectoria t JOIN equipos eq ON eq.id = t.equipo_id
                 WHERE t.jugador_id = j.id AND t.fecha_fin IS NULL
                 ORDER BY t.temporada DESC LIMIT 1) AS equipo_actual
        FROM jugadores j
        LEFT JOIN posiciones p ON p.id = j.posicion_id
        WHERE j.estado_actual_id = (SELECT id FROM estados_jugador WHERE nombre = 'Activo');
        """,
        conn,
    )
    df = jugadores.merge(agregado, on="jugador_id", how="inner")
    inicio = pd.to_numeric(df["temporada"].str[:4], errors="coerce")
    nacimiento = pd.to_datetime(df["fecha_nacimiento"], errors="coerce").dt.year
    df["edad_en_temporada"] = inicio - nacimiento
    df["pir_proyectado"] = df["pir_base"] + df["edad_en_temporada"].fillna(26).map(_ajuste_por_edad)
    return df.sort_values("pir_proyectado", ascending=False)


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        print(generar_proyecciones(conn)[
            ["nombre", "apellidos", "posicion", "equipo_actual", "temporada",
             "edad_en_temporada", "pir_origen", "pir_proyectado"]
        ].head(20).to_string(index=False))
