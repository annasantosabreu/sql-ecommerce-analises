-- 07. Ranking de vendedores dentro de cada categoria.
-- Receita calculada pelo preco do produto no item, sem frete.

WITH desempenho AS (
    SELECT
        c.id AS categoria_id,
        c.nome AS categoria,
        v.id AS vendedor_id,
        v.estado AS estado_vendedor,
        COUNT(DISTINCT p.id) AS pedidos,
        COUNT(*) AS itens_vendidos,
        SUM(i.preco)::numeric(14, 2) AS receita_produtos
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN vendedores v ON v.id = i.vendedor_id
    JOIN produtos pr ON pr.id = i.produto_id
    JOIN categorias c ON c.id = pr.categoria_id
    WHERE p.status <> 'cancelado'
    GROUP BY c.id, c.nome, v.id, v.estado
)
SELECT
    categoria_id,
    categoria,
    vendedor_id,
    estado_vendedor,
    pedidos,
    itens_vendidos,
    receita_produtos,
    RANK() OVER (
        PARTITION BY categoria_id
        ORDER BY receita_produtos DESC
    ) AS ranking_na_categoria
FROM desempenho
ORDER BY categoria, ranking_na_categoria, vendedor_id;
