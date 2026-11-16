-- Prazo e atraso por estado; apenas pedidos entregues com datas disponíveis.
SELECT cl.estado,
       COUNT(*) AS entregas,
       AVG(EXTRACT(EPOCH FROM (p.data_entrega - p.data_compra)) / 86400.0)::NUMERIC(10,2) AS prazo_medio_dias,
       AVG(GREATEST(0, EXTRACT(EPOCH FROM (p.data_entrega - p.data_estimada_entrega)) / 86400.0))::NUMERIC(10,2) AS atraso_medio_dias,
       COUNT(*) FILTER (WHERE p.data_entrega > p.data_estimada_entrega) AS entregas_atrasadas
FROM pedidos p
JOIN clientes cl ON cl.id = p.cliente_id
WHERE p.status = 'entregue'
  AND p.data_entrega IS NOT NULL
GROUP BY cl.estado
ORDER BY atraso_medio_dias DESC;
