-- Receita por categoria. Cada item aparece uma única vez na agregação.
SELECT c.nome AS categoria,
       COUNT(DISTINCT p.id) AS pedidos,
       SUM(i.preco + i.frete)::NUMERIC(14,2) AS faturamento,
       SUM(i.preco)::NUMERIC(14,2) AS valor_produtos
FROM pedidos p
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN produtos pr ON pr.id = i.produto_id
JOIN categorias c ON c.id = pr.categoria_id
WHERE p.status = 'entregue'
GROUP BY c.id, c.nome
ORDER BY faturamento DESC;
