# Análises SQL — etapa 1

As oito consultas desta pasta foram construídas para o schema em `sql/00_schema.sql`.

## Definições usadas

- **Receita de produtos:** `SUM(itens_pedido.preco)`. O frete é apresentado separadamente.
- **Valor dos pedidos com frete:** soma de `preco + frete` por item.
- **Pedidos comerciais:** pedidos cujo status é diferente de `cancelado`.
- **Distribuição de status:** inclui todos os pedidos, inclusive os cancelados.
- **Ticket por categoria:** receita dos itens daquela categoria dividida pelo número de pedidos distintos que contêm a categoria. Um pedido com mais de uma categoria participa do denominador de cada categoria comprada.
- **Entrega atrasada:** `data_entrega > data_estimada_entrega`.
- **Estado nas análises geográficas:** estado do cadastro do cliente.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `01_faturamento_mensal.sql` | Receita mensal, frete, ticket e variação mensal |
| `02_media_movel.sql` | Série mensal e média móvel de três meses |
| `03_ticket_categoria_mes.sql` | Ticket médio por mês e categoria |
| `04_distribuicao_status.sql` | Participação dos pedidos por status |
| `05_pareto_categoria.sql` | Receita, participação e Pareto por categoria |
| `06_receita_estado.sql` | Receita e participação por estado do cliente |
| `07_ranking_vendedores_categoria.sql` | Ranking de vendedores dentro de cada categoria |
| `08_entrega_estado.sql` | Prazo e percentual de atraso por estado |

## Execução manual

Na raiz do repositório, com o container `banco` em execução:

```powershell
Get-ChildItem sql/03_analises/*.sql | Where-Object Name -ne "README.md" | Sort-Object Name | ForEach-Object {
    Write-Host "Executando $($_.Name)"
    docker compose exec -T banco psql -v ON_ERROR_STOP=1 -U ecommerce -d ecommerce -f "/sql/03_analises/$($_.Name)"
}
```

Ou execute individualmente:

```bash
docker compose exec banco psql -U ecommerce -d ecommerce -f /sql/03_analises/01_faturamento_mensal.sql
```

As consultas são `SELECT` e não modificam os dados.
