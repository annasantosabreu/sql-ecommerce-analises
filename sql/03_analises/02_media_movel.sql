-- 02. Media movel de tres meses do faturamento de produtos.
-- Meses sem pedidos sao incluidos com valor zero para manter a janela temporal.

WITH limites AS (
    SELECT
        DATE_TRUNC('month', MIN(data_compra))::date AS primeiro_mes,
        DATE_TRUNC('month', MAX(data_compra))::date AS ultimo_mes
    FROM pedidos
),
calendario AS (
    SELECT GENERATE_SERIES(primeiro_mes, ultimo_mes, INTERVAL '1 month')::date AS mes
    FROM limites
    WHERE primeiro_mes IS NOT NULL
),
mensal AS (
    SELECT
        DATE_TRUNC('month', p.data_compra)::date AS mes,
        SUM(i.preco)::numeric(14, 2) AS receita_produtos
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status <> 'cancelado'
    GROUP BY DATE_TRUNC('month', p.data_compra)::date
),
serie AS (
    SELECT
        c.mes,
        COALESCE(m.receita_produtos, 0)::numeric(14, 2) AS receita_produtos
    FROM calendario c
    LEFT JOIN mensal m USING (mes)
)
SELECT
    mes,
    receita_produtos,
    ROUND(
        AVG(receita_produtos) OVER (
            ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS media_movel_3_meses
FROM serie
ORDER BY mes;
