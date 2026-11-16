-- Ranking de vendedores por valor dos itens vendidos em pedidos entregues.
SELECT v.id AS vendedor_id,
       v.estado,
       COUNT(DISTINCT p.id) AS pedidos,
       SUM(i.preco)::NUMERIC(14,2) AS valor_produtos
FROM pedidos p
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN vendedores v ON v.id = i.vendedor_id
WHERE p.status = 'entregue'
GROUP BY v.id, v.estado
ORDER BY valor_produtos DESC
LIMIT 10;
