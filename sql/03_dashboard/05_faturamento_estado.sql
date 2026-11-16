-- Faturamento de pedidos entregues por estado do cliente.
SELECT cl.estado,
       COUNT(DISTINCT p.id) AS pedidos,
       SUM(i.preco + i.frete)::NUMERIC(14,2) AS faturamento
FROM pedidos p
JOIN clientes cl ON cl.id = p.cliente_id
JOIN itens_pedido i ON i.pedido_id = p.id
WHERE p.status = 'entregue'
GROUP BY cl.estado
ORDER BY faturamento DESC;
