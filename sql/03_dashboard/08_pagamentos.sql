-- Distribuição dos meios de pagamento em pedidos entregues.
SELECT pg.tipo,
       COUNT(DISTINCT p.id) AS pedidos,
       SUM(pg.valor)::NUMERIC(14,2) AS valor_pago,
       AVG(pg.parcelas)::NUMERIC(10,2) AS media_parcelas
FROM pedidos p
JOIN pagamentos pg ON pg.pedido_id = p.id
WHERE p.status = 'entregue'
GROUP BY pg.tipo
ORDER BY valor_pago DESC;
