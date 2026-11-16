-- 05. Receita de produtos por categoria e participacao acumulada (Pareto).
-- Pedidos cancelados sao excluidos. Frete nao compoe a receita de produtos.

WITH receita AS (
    SELECT
        c.id AS categoria_id,
        c.nome AS categoria,
        SUM(i.preco)::numeric(14, 2) AS receita_produtos,
        COUNT(DISTINCT p.id) AS pedidos_com_categoria,
        COUNT(*) AS itens_vendidos
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr ON pr.id = i.produto_id
    JOIN categorias c ON c.id = pr.categoria_id
    WHERE p.status <> 'cancelado'
    GROUP BY c.id, c.nome
),
acumulado AS (
    SELECT
        *,
        SUM(receita_produtos) OVER (
            ORDER BY receita_produtos DESC, categoria
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS receita_acumulada,
        SUM(receita_produtos) OVER () AS receita_total
    FROM receita
)
SELECT
    categoria_id,
    categoria,
    pedidos_com_categoria,
    itens_vendidos,
    receita_produtos,
    ROUND(100 * receita_produtos / NULLIF(receita_total, 0), 2) AS participacao_percentual,
    ROUND(100 * receita_acumulada / NULLIF(receita_total, 0), 2) AS participacao_acumulada_percentual
FROM acumulado
ORDER BY receita_produtos DESC, categoria;
