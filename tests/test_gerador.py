"""Testes automatizados do gerador sintetico (stdlib unittest)."""

from __future__ import annotations

import csv
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import numpy as np

from generator.config import Configuracao
from generator.gerar_dados import distribuicao_pedidos_por_cliente, gerar


class TestDistribuicaoPedidos(unittest.TestCase):
    def test_configuracao_rejeita_pedidos_insuficientes_para_recorrencia(self) -> None:
        cfg = replace(Configuracao(), volume_clientes=100, volume_pedidos=100)
        with self.assertRaisesRegex(ValueError, "segunda compra"):
            cfg.validar()

    def test_quantidade_total_e_percentual_recorrente(self) -> None:
        cfg = replace(
            Configuracao(),
            volume_clientes=200,
            volume_pedidos=1000,
            percentual_recorrentes=0.175,
        )
        contagens = distribuicao_pedidos_por_cliente(cfg, np.random.default_rng(cfg.semente))
        self.assertEqual(len(contagens), cfg.volume_clientes)
        self.assertEqual(sum(contagens), cfg.volume_pedidos)
        self.assertEqual(sum(1 for quantidade in contagens if quantidade > 1), 35)
        self.assertTrue(all(quantidade >= 1 for quantidade in contagens))


class TestGeracaoArquivos(unittest.TestCase):
    def test_arquivos_e_conciliacao_financeira(self) -> None:
        with tempfile.TemporaryDirectory() as diretorio:
            cfg = replace(
                Configuracao(),
                semente=123,
                volume_clientes=60,
                volume_vendedores=8,
                volume_categorias=8,
                volume_produtos=80,
                volume_pedidos=180,
                percentual_recorrentes=0.15,
                diretorio_saida=Path(diretorio),
            )
            contagens = gerar(cfg)
            self.assertEqual(contagens["pedidos"], 180)
            self.assertTrue((Path(diretorio) / "manifesto.json").exists())

            with (Path(diretorio) / "itens_pedido.csv").open(encoding="utf-8", newline="") as arquivo:
                itens = list(csv.DictReader(arquivo, delimiter=";"))
            with (Path(diretorio) / "pagamentos.csv").open(encoding="utf-8", newline="") as arquivo:
                pagamentos = list(csv.DictReader(arquivo, delimiter=";"))

            totais: dict[str, Decimal] = {}
            for item in itens:
                pedido_id = item["pedido_id"]
                totais[pedido_id] = totais.get(pedido_id, Decimal("0.00")) + Decimal(item["preco"]) + Decimal(item["frete"])
            self.assertEqual(len(pagamentos), 180)
            for pagamento in pagamentos:
                self.assertEqual(totais[pagamento["pedido_id"]], Decimal(pagamento["valor"]))


if __name__ == "__main__":
    unittest.main()
