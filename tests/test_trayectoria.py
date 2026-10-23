import unittest

from scraping.trayectoria import parsear_trayectoria

FIXTURE = """
<div><span>2025 - 2026</span><p>Costa Norte Basket</p></div>
<div><span>2024 - 2025</span><p>Atlético Meseta</p></div>
<div><span>Texto suelto</span></div>
"""


class TestTrayectoria(unittest.TestCase):
    def test_extrae_etapas_en_orden(self):
        self.assertEqual(
            parsear_trayectoria(FIXTURE),
            [{"temporada": "2025-2026", "equipo": "Costa Norte Basket"},
             {"temporada": "2024-2025", "equipo": "Atlético Meseta"}],
        )

    def test_html_sin_patron(self):
        self.assertEqual(parsear_trayectoria("<p>nada</p>"), [])


if __name__ == "__main__":
    unittest.main()
