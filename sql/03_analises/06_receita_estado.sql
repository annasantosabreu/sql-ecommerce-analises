-- 06. Receita de produtos por estado do cliente.
-- O estado e obtido pelo cadastro do cliente vinculado ao pedido.

SELECT
    cl.estado,
    COUNT(DISTINCT p.id) AS pedidos,
    COUNT(DISTINCT p.cliente_id) AS clientes,
    SUM(i.preco)::numeric(14, 2) AS receita_produtos,
    SUM(i.frete)::numeric(14, 2) AS frete,
    ROUND(
        100 * SUM(i.preco) / NULLIF(SUM(SUM(i.preco)) OVER (), 0),
        2
    ) AS participacao_receita_percentual,
    RANK() OVER (ORDER BY SUM(i.preco) DESC) AS posicao_receita
FROM pedidos p
JOIN clientes cl ON cl.id = p.cliente_id
JOIN itens_pedido i ON i.pedido_id = p.id
WHERE p.status <> 'cancelado'
GROUP BY cl.estado
ORDER BY receita_produtos DESC, cl.estado;
