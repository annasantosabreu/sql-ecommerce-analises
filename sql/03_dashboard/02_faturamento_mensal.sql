-- Faturamento mensal por data da compra; somente pedidos entregues.
SELECT
    DATE_TRUNC('month', p.data_compra)::DATE AS mes,
    COUNT(DISTINCT p.id) AS pedidos,
    SUM(i.preco + i.frete)::NUMERIC(14,2) AS faturamento,
    AVG(totais.valor_pedido)::NUMERIC(14,2) AS ticket_medio
FROM pedidos p
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN (
    SELECT pedido_id, SUM(preco + frete) AS valor_pedido
    FROM itens_pedido
    GROUP BY pedido_id
) totais ON totais.pedido_id = p.id
WHERE p.status = 'entregue'
GROUP BY DATE_TRUNC('month', p.data_compra)
ORDER BY mes;
