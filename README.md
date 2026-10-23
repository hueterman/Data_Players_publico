# Seguimiento de jugadores de baloncesto — versión pública (demo)

Aplicación para llevar la **ficha individual de cada jugador**: trayectoria de
equipos, estadísticas por temporada, diario de lesiones, datos económicos y
otros hitos de carrera. Combina scraping de fuentes públicas con una interfaz
web (Flask) para completar y corregir los datos a mano.

> Esta es la **versión pública de demostración**: enseña la arquitectura, el
> modelo de datos y un scraper completo, pero **no** incluye los conectores de
> todas las ligas, la reconciliación de jugadores entre fuentes, el pipeline
> analítico completo ni datos reales. Todos los datos de ejemplo son ficticios.

## Qué incluye

| Parte | Estado |
|---|---|
| Modelo de datos (SQLite, ~20 tablas con catálogos editables) | Completo |
| Aplicación Flask: fichas, búsqueda por estadísticas, lesiones, datos económicos | Completa |
| Scraper de trayectoria + tests con fixture | Completo |
| Base común de scraping (sesión, reintentos, parseo de tablas) | Completa |
| Proyección de rendimiento | **Línea base** (media ponderada + edad) |
| Conectores de estadísticas y de otras ligas | Solo interfaz |
| Métricas por 100 posesiones y z-score por liga | Solo interfaz |
| Reconciliación de duplicados entre fuentes, búsqueda de texto (FTS5) | Versión completa |

## Estructura

```
config.py               rutas centrales
database/schema.sql     modelo de datos
database/init_db.py     crea la BD desde el esquema
db/conexion.py          conexión y helpers de catálogos/equipos
scraping/               base_scraper + trayectoria (completo) + stubs
analitica/              proyecciones (línea base) + stub de métricas
formularios/            app Flask (rutas, plantillas, estilos)
seed_demo.py            datos ficticios de demostración
tests/                  tests del parser
```

## Puesta en marcha

```bash
pip install -r requirements.txt
python -m database.init_db --reset
python seed_demo.py          # 24 jugadores ficticios
python run.py                # http://localhost:5500
python -m unittest discover -s tests -t .
```

## Ideas de diseño que conviene destacar

- **Catálogos cerrados como tablas**, editables sin tocar el esquema.
- **Procedencia y fiabilidad de cada dato** (`fuentes`, `niveles_fiabilidad`):
  distingue lo confirmado de lo estimado o los rumores.
- **Idempotencia**: índices únicos + `ON CONFLICT` para poder relanzar el
  scraping sin duplicar filas.
- **Parseo por patrón de texto** en vez de selectores CSS frágiles, probado
  contra fixtures locales.

## Scraping responsable

Revisa los términos de uso y el `robots.txt` de cada sitio antes de apuntar un
scraper a él, limita la frecuencia de peticiones y no redistribuyas datos
sujetos a derechos.

## Licencia

[PolyForm Noncommercial 1.0.0](LICENSE): puedes leer, estudiar y modificar el
código para uso no comercial. El uso comercial requiere permiso del autor.

Autor: Pedro Huete Toral.
