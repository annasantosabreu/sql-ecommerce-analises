-- 03. Ticket medio de produtos por mes e categoria.
-- O denominador conta pedidos distintos que compraram aquela categoria;
-- um pedido com duas categorias aparece em cada categoria correspondente.

SELECT
    DATE_TRUNC('month', p.data_compra)::date AS mes,
    c.id AS categoria_id,
    c.nome AS categoria,
    COUNT(DISTINCT p.id) AS pedidos_com_categoria,
    SUM(i.preco)::numeric(14, 2) AS receita_produtos,
    SUM(i.frete)::numeric(14, 2) AS frete,
    ROUND(SUM(i.preco) / NULLIF(COUNT(DISTINCT p.id), 0), 2) AS ticket_medio_categoria
FROM pedidos p
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN produtos pr ON pr.id = i.produto_id
JOIN categorias c ON c.id = pr.categoria_id
WHERE p.status <> 'cancelado'
GROUP BY DATE_TRUNC('month', p.data_compra)::date, c.id, c.nome
ORDER BY mes, receita_produtos DESC;
