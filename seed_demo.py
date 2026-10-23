"""
Carga datos FICTICIOS de demostración (jugadores, equipos, estadísticas,
trayectoria, lesiones y datos económicos inventados). Ningún dato real.

    python -m database.init_db --reset
    python seed_demo.py
"""
import random
import sqlite3
from datetime import date

from config import DB_PATH

random.seed(42)

NOMBRES = ["Adrián", "Bruno", "Carlos", "Diego", "Eloy", "Fabián", "Gonzalo", "Héctor",
           "Iván", "Jorge", "Koldo", "Luis", "Mateo", "Nico", "Óscar", "Pablo",
           "Quique", "Rubén", "Sergio", "Tomás", "Unai", "Víctor", "Xavi", "Yeray"]
APELLIDOS = ["Marín", "Ledesma", "Aranda", "Bellido", "Cortés", "Duarte", "Escobar", "Fontán",
             "Garrido", "Hidalgo", "Ibarra", "Jaramillo", "Lozano", "Montero", "Nieto", "Ochoa",
             "Paredes", "Quintana", "Robles", "Sandoval", "Tejada", "Uribe", "Valdés", "Zamora"]
EQUIPOS = [("Costa Norte Basket", "Puertoverde"), ("Atlético Meseta", "Villaalta"),
           ("Real Sierra BC", "Montefrío"), ("Delta del Sur", "Isla Real"),
           ("Levante Albatros", "Marbella Alta"), ("Pirineo Lobos", "Alto Valle")]
COMPETICION = "Liga Demo"
TEMPORADAS = ["2023-2024", "2024-2025", "2025-2026", "2026-2027"]
# (tipo, zona, gravedad, texto)
LESIONES = [("Ligamentosa", "Tobillo", "Leve"), ("Muscular", "Isquiotibial", "Moderada"),
            ("Articular", "Rodilla", "Grave"), ("Ósea", "Mano", "Moderada")]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cat = lambda t, n: conn.execute(f"SELECT id FROM {t} WHERE nombre = ?;", (n,)).fetchone()[0]
    posiciones = [r[0] for r in conn.execute("SELECT id FROM posiciones ORDER BY id;")]

    equipo_ids = []
    for nombre, ciudad in EQUIPOS:
        cur = conn.execute(
            "INSERT INTO equipos (nombre, pais, ciudad, competicion, nivel) VALUES (?, 'España', ?, ?, 'Primera');",
            (nombre, ciudad, COMPETICION),
        )
        equipo_ids.append(cur.lastrowid)

    n = len(NOMBRES)
    for i in range(n):
        nacimiento = date(random.randint(1993, 2005), random.randint(1, 12), random.randint(1, 28))
        pos = posiciones[i % len(posiciones)]
        altura = 178 + (pos - 1) * 7 + random.randint(-3, 3)
        cur = conn.execute(
            """INSERT INTO jugadores (nombre, apellidos, fecha_nacimiento, nacionalidad,
                                      posicion_id, altura_cm, peso_kg, estado_actual_id)
               VALUES (?, ?, ?, 'España', ?, ?, ?, ?);""",
            (NOMBRES[i], APELLIDOS[(i * 7) % n], nacimiento.isoformat(), pos, altura,
             altura - 100 + random.randint(-4, 8), cat("estados_jugador", "Activo")),
        )
        jid = cur.lastrowid

        base = random.uniform(5, 16) + (2 if i % 5 == 0 else 0)
        equipo_actual = random.choice(equipo_ids)
        for k, temporada in enumerate(TEMPORADAS):
            equipo = equipo_actual if k >= 2 else random.choice(equipo_ids)
            pj = random.randint(18, 34)
            mins = random.uniform(12, 31)
            pts = max(2.0, base * random.uniform(0.8, 1.1) * mins / 25)
            reb = max(0.8, (pos / 5) * 6 * mins / 25 + random.uniform(-0.5, 0.8))
            ast = max(0.4, (6 - pos) / 5 * 5 * mins / 25 + random.uniform(-0.4, 0.6))
            pir = pts + reb + ast - random.uniform(1, 3)
            conn.execute(
                """INSERT INTO estadisticas_temporada
                   (jugador_id, equipo_id, temporada, competicion, partidos_jugados,
                    minutos_promedio, puntos_promedio, rebotes_promedio, asistencias_promedio,
                    valoracion_pir, fuente_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?);""",
                (jid, equipo, temporada, COMPETICION, pj, round(mins, 1), round(pts, 1),
                 round(reb, 1), round(ast, 1), round(pir, 1), cat("fuentes", "Estimado")),
            )
            conn.execute(
                """INSERT OR IGNORE INTO trayectoria (jugador_id, equipo_id, temporada, fecha_fin)
                   VALUES (?,?,?,?);""",
                (jid, equipo, temporada, None if k == len(TEMPORADAS) - 1 else f"{temporada[-4:]}-06-30"),
            )

        if i % 4 == 0:
            tipo, zona, grav = random.choice(LESIONES)
            conn.execute(
                """INSERT INTO lesiones (jugador_id, fecha_inicio, fecha_fin_real, tipo_lesion,
                                         zona_corporal, gravedad_id, estado_id, fuente_id, fiabilidad_id, notas)
                   VALUES (?, '2025-11-10', '2025-12-20', ?, ?, ?, ?, ?, ?, 'Dato ficticio de demostración');""",
                (jid, tipo, zona, cat("grados_gravedad", grav), cat("estados_lesion", "Recuperado"),
                 cat("fuentes", "Manual"), cat("niveles_fiabilidad", "Estimado")),
            )
        if i % 3 == 0:
            conn.execute(
                """INSERT INTO datos_economicos (jugador_id, equipo_id, temporada, tipo_contrato_id,
                                                 salario_estimado, notas)
                   VALUES (?,?,?,?,?, 'Dato ficticio de demostración');""",
                (jid, equipo_actual, TEMPORADAS[-1], cat("tipos_contrato", "Profesional"),
                 random.randint(4, 15) * 10000),
            )
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM jugadores;").fetchone()[0]
    print(f"Datos de demostración cargados: {total} jugadores ficticios.")


if __name__ == "__main__":
    main()
