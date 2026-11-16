"""Configuracoes do gerador de dados sinteticos.

As variaveis de ambiente permitem reduzir o volume para testes sem alterar o codigo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Configuracao:
    semente: int = int(os.getenv("SEMENTE", "20261116"))
    volume_clientes: int = int(os.getenv("VOLUME_CLIENTES", "20000"))
    volume_vendedores: int = int(os.getenv("VOLUME_VENDEDORES", "300"))
    volume_categorias: int = int(os.getenv("VOLUME_CATEGORIAS", "50"))
    volume_produtos: int = int(os.getenv("VOLUME_PRODUTOS", "3000"))
    volume_pedidos: int = int(os.getenv("VOLUME_PEDIDOS", "100000"))
    percentual_recorrentes: float = float(os.getenv("PERCENTUAL_CLIENTES_RECORRENTES", "0.175"))
    data_inicio: date = date.fromisoformat(os.getenv("DATA_INICIO", "2024-11-01"))
    data_fim: date = date.fromisoformat(os.getenv("DATA_FIM", "2026-10-31"))
    diretorio_saida: Path = Path(os.getenv("DIRETORIO_DADOS", "data/gerados"))

    def validar(self) -> None:
        """Impede configuracoes inconsistentes antes de criar qualquer arquivo."""
        volumes = {
            "volume_clientes": self.volume_clientes,
            "volume_vendedores": self.volume_vendedores,
            "volume_categorias": self.volume_categorias,
            "volume_produtos": self.volume_produtos,
            "volume_pedidos": self.volume_pedidos,
        }
        invalidos = [nome for nome, valor in volumes.items() if valor <= 0]
        if invalidos:
            raise ValueError(f"Volumes devem ser positivos: {', '.join(invalidos)}")
        if self.volume_clientes < 2:
            raise ValueError("O volume de clientes deve ser pelo menos 2.")
        if not 0 < self.percentual_recorrentes < 1:
            raise ValueError("PERCENTUAL_CLIENTES_RECORRENTES deve estar entre 0 e 1.")
        minimo_pedidos = self.volume_clientes + round(
            self.volume_clientes * self.percentual_recorrentes
        )
        if self.volume_pedidos < minimo_pedidos:
            raise ValueError(
                "O volume de pedidos deve comportar pelo menos uma compra por cliente "
                "e uma segunda compra para cada cliente recorrente configurado "
                f"(minimo: {minimo_pedidos})."
            )
        if self.data_inicio >= self.data_fim:
            raise ValueError("DATA_INICIO deve ser anterior a DATA_FIM.")
        if self.volume_categorias > len(NOMES_CATEGORIAS):
            raise ValueError(
                f"O gerador possui {len(NOMES_CATEGORIAS)} categorias. "
                "Reduza VOLUME_CATEGORIAS ou amplie NOMES_CATEGORIAS."
            )


NOMES_CATEGORIAS = [
    "Acessorios para celulares", "Acessorios para computadores", "Acessorios para fotografia",
    "Acessorios para veiculos", "Alimentos e bebidas", "Artigos de papelaria", "Audio",
    "Automacao residencial", "Bebe", "Beleza", "Brinquedos", "Cama e banho", "Cameras",
    "Casa e decoracao", "Ciclismo", "Colecionaveis", "Construcao e ferramentas", "Cozinha",
    "Cuidados pessoais", "Decoracao de jardim", "Eletrodomesticos", "Eletronicos", "Esporte",
    "Games", "Iluminacao", "Informatica", "Instrumentos musicais", "Jardinagem", "Livros",
    "Malas e mochilas", "Moveis", "Organizacao", "Outdoors e camping", "Papelaria criativa",
    "Pet shop", "Roupas femininas", "Roupas masculinas", "Calcados", "Saude e bem-estar",
    "Seguranca residencial", "Telefonia", "TV e video", "Utensilios domesticos", "Utilidades",
    "Relogios", "Joias e bijuterias", "Suprimentos para escritorio", "Suprimentos para impressao",
    "Acessorios esportivos", "Produtos sustentaveis",
]


if __name__ == "__main__":
    cfg = Configuracao()
    cfg.validar()
    print(cfg)
