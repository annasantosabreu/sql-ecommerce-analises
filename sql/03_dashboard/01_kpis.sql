-- KPIs gerais. Receita considera pedidos entregues e inclui frete.
WITH pedidos_entregues AS (
    SELECT p.id, p.cliente_id,
           SUM(i.preco + i.frete) AS valor_pedido,
           MIN(p.data_compra) AS data_compra,
           MIN(p.data_entrega) AS data_entrega
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    WHERE p.status = 'entregue'
    GROUP BY p.id, p.cliente_id
)
SELECT
    (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
    COUNT(*) AS pedidos_entregues,
    COUNT(DISTINCT cliente_id) AS clientes_com_compra_entregue,
    COALESCE(SUM(valor_pedido), 0)::NUMERIC(14,2) AS faturamento_entregue,
    COALESCE(AVG(valor_pedido), 0)::NUMERIC(14,2) AS ticket_medio,
    COALESCE(AVG(EXTRACT(EPOCH FROM (data_entrega - data_compra)) / 86400.0), 0)::NUMERIC(10,2) AS prazo_medio_dias
FROM pedidos_entregues;
