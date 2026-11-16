"""Executa as consultas analiticas e exporta seus resultados para JSON.

Uso (na raiz do repositorio):
    python -m pip install -r dashboard/requirements.txt
    python dashboard/exportar_dashboard.py

O arquivo gerado contem somente resultados agregados. Credenciais nunca sao exportadas.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql" / "03_analises"
OUTPUT = ROOT / "data" / "dashboard.json"

QUERIES = {
    "faturamento_mensal": "01_faturamento_mensal.sql",
    "media_movel": "02_media_movel.sql",
    "ticket_categoria_mes": "03_ticket_categoria_mes.sql",
    "distribuicao_status": "04_distribuicao_status.sql",
    "pareto_categoria": "05_pareto_categoria.sql",
    "receita_estado": "06_receita_estado.sql",
    "ranking_vendedores_categoria": "07_ranking_vendedores_categoria.sql",
    "entrega_estado": "08_entrega_estado.sql",
}


def carregar_env_local() -> None:
    """Carrega pares KEY=VALUE do .env sem sobrescrever variaveis existentes."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for linha in env_path.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def serializar(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    raise TypeError(f"Tipo nao serializavel: {type(valor).__name__}")


def conexao():
    carregar_env_local()
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "ecommerce")),
        user=os.getenv("PGUSER", os.getenv("POSTGRES_USER", "ecommerce")),
        password=os.getenv("PGPASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
        connect_timeout=10,
        row_factory=dict_row,
    )


def main() -> None:
    resultados: dict[str, list[dict[str, Any]]] = {}
    with conexao() as conn:
        for chave, nome_arquivo in QUERIES.items():
            caminho = SQL_DIR / nome_arquivo
            if not caminho.is_file():
                raise FileNotFoundError(f"Consulta nao encontrada: {caminho}")
            sql = caminho.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                cur.execute(sql)
                resultados[chave] = [dict(linha) for linha in cur.fetchall()]

    payload = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "synthetic_data": True,
            "source": "PostgreSQL 16",
            "query_count": len(QUERIES),
            "definitions": {
                "revenue": "Soma de itens_pedido.preco; frete exibido separadamente.",
                "commercial_orders": "Pedidos com status diferente de cancelado.",
                "delivery_delay": "Data de entrega posterior a data estimada.",
            },
        },
        "queries": resultados,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporario = OUTPUT.with_suffix(".json.tmp")
    temporario.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=serializar) + "\n",
        encoding="utf-8",
    )
    temporario.replace(OUTPUT)
    print(f"Dashboard atualizado: {OUTPUT.relative_to(ROOT)}")
    print(f"Consultas exportadas: {len(resultados)}")
    print(f"Linhas exportadas: {sum(len(rows) for rows in resultados.values()):,}")


if __name__ == "__main__":
    try:
        main()
    except psycopg.OperationalError as exc:
        raise SystemExit(
            "Nao foi possivel conectar ao PostgreSQL. Verifique o Docker, o container "
            "'banco' e as credenciais do arquivo .env.\n"
            f"Detalhe: {exc}"
        ) from exc
