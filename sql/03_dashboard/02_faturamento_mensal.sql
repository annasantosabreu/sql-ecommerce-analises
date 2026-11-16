-- Faturamento mensal por data da compra; somente pedidos entregues.
WITH por_pedido AS (
    SELECT p.id,
           DATE_TRUNC('month', p.data_compra)::DATE AS mes,
           SUM(i.preco + i.frete) AS valor_pedido
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status = 'entregue'
    GROUP BY p.id, DATE_TRUNC('month', p.data_compra)::DATE
)
SELECT mes,
       COUNT(*) AS pedidos,
       SUM(valor_pedido)::NUMERIC(14,2) AS faturamento,
       AVG(valor_pedido)::NUMERIC(14,2) AS ticket_medio
FROM por_pedido
GROUP BY mes
ORDER BY mes;
