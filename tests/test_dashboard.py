"""Validacoes estruturais do pacote do dashboard."""
from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path

from dashboard.exportar import QUERIES, SQL_DIR, serializar


class TestDashboardExportacao(unittest.TestCase):
    def test_existencia_das_oito_consultas(self) -> None:
        self.assertEqual(len(QUERIES), 8)
        for arquivo in QUERIES.values():
            with self.subTest(arquivo=arquivo):
                self.assertTrue((SQL_DIR / arquivo).is_file())

    def test_consultas_nao_estao_vazias(self) -> None:
        for arquivo in QUERIES.values():
            with self.subTest(arquivo=arquivo):
                self.assertTrue((SQL_DIR / arquivo).read_text(encoding="utf-8").strip())

    def test_serializacao_de_decimal(self) -> None:
        self.assertEqual(serializar(Decimal("123.45")), 123.45)


if __name__ == "__main__":
    unittest.main()
