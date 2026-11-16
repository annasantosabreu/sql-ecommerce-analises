"""Exporta as consultas do dashboard para JSON a partir do PostgreSQL.

Uso: python -m dashboard.exportar
Configuração: DATABASE_URL ou PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql" / "03_dashboard"
OUTPUT = ROOT / "data" / "dashboard.json"
load_dotenv(ROOT / ".env")

QUERIES = {
    "kpis": "01_kpis.sql",
    "faturamento_mensal": "02_faturamento_mensal.sql",
    "categorias": "03_categorias.sql",
    "status_pedidos": "04_status_pedidos.sql",
    "faturamento_estado": "05_faturamento_estado.sql",
    "top_vendedores": "06_top_vendedores.sql",
    "entregas_estado": "07_entregas_estado.sql",
    "pagamentos": "08_pagamentos.sql",
}


def serializar(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return valor


def carregar_consulta(cursor: psycopg.Cursor, caminho: Path) -> list[dict[str, Any]]:
    cursor.execute(caminho.read_text(encoding="utf-8"))
    return [
        {chave: serializar(valor) for chave, valor in linha.items()}
        for linha in cursor.fetchall()
    ]


def main() -> None:
    ausentes = [nome for nome in QUERIES.values() if not (SQL_DIR / nome).is_file()]
    if ausentes:
        raise FileNotFoundError(f"Consultas SQL ausentes: {', '.join(ausentes)}")

    dados: dict[str, Any] = {
        "metadata": {
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "source": "PostgreSQL",
            "revenue_definition": "Pedidos entregues; soma de preço dos itens e frete.",
        }
    }

    dsn = os.getenv("DATABASE_URL")
    conexao = psycopg.connect(dsn) if dsn else psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "ecommerce"),
        user=os.getenv("PGUSER", "ecommerce"),
        password=os.getenv("PGPASSWORD", ""),
    )
    with conexao, conexao.cursor(row_factory=dict_row) as cursor:
        for chave, arquivo in QUERIES.items():
            dados[chave] = carregar_consulta(cursor, SQL_DIR / arquivo)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporario = OUTPUT.with_suffix(".json.tmp")
    temporario.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    temporario.replace(OUTPUT)
    print(f"Dashboard atualizado: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
