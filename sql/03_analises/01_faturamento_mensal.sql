-- 01. Evolucao mensal do faturamento de produtos.
-- Receita = soma de itens_pedido.preco. Frete e valor total com frete
-- ficam separados. Pedidos cancelados sao excluidos das metricas comerciais.

WITH mensal AS (
    SELECT
        DATE_TRUNC('month', p.data_compra)::date AS mes,
        COUNT(DISTINCT p.id) AS pedidos,
        COUNT(DISTINCT p.cliente_id) AS clientes_unicos,
        SUM(i.preco)::numeric(14, 2) AS receita_produtos,
        SUM(i.frete)::numeric(14, 2) AS frete,
        SUM(i.preco + i.frete)::numeric(14, 2) AS valor_pedidos_com_frete
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status <> 'cancelado'
    GROUP BY DATE_TRUNC('month', p.data_compra)::date
)
SELECT
    mes,
    pedidos,
    clientes_unicos,
    receita_produtos,
    frete,
    valor_pedidos_com_frete,
    ROUND(receita_produtos / NULLIF(pedidos, 0), 2) AS ticket_medio_produtos,
    receita_produtos - LAG(receita_produtos) OVER (ORDER BY mes) AS variacao_absoluta,
    ROUND(
        100 * (receita_produtos / NULLIF(LAG(receita_produtos) OVER (ORDER BY mes), 0) - 1),
        2
    ) AS variacao_percentual
FROM mensal
ORDER BY mes;
