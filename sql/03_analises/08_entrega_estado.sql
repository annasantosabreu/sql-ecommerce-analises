-- 08. Prazo e atraso de entrega por estado do cliente.
-- Considera somente pedidos entregues com as duas datas de entrega presentes.
-- Atraso positivo significa entrega posterior a data estimada.

WITH entregas AS (
    SELECT
        cl.estado,
        p.id AS pedido_id,
        EXTRACT(EPOCH FROM (p.data_entrega - p.data_compra)) / 86400.0 AS dias_ate_entrega,
        EXTRACT(EPOCH FROM (p.data_entrega - p.data_estimada_entrega)) / 86400.0 AS diferenca_estimativa_dias,
        (p.data_entrega > p.data_estimada_entrega) AS entregue_com_atraso
    FROM pedidos p
    JOIN clientes cl ON cl.id = p.cliente_id
    WHERE p.status = 'entregue'
      AND p.data_entrega IS NOT NULL
      AND p.data_estimada_entrega IS NOT NULL
)
SELECT
    estado,
    COUNT(*) AS pedidos_entregues,
    ROUND(AVG(dias_ate_entrega)::numeric, 2) AS media_dias_ate_entrega,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY dias_ate_entrega)::numeric,
        2
    ) AS mediana_dias_ate_entrega,
    ROUND(
        AVG(GREATEST(diferenca_estimativa_dias, 0))::numeric,
        2
    ) AS media_dias_de_atraso,
    COUNT(*) FILTER (WHERE entregue_com_atraso) AS entregas_atrasadas,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE entregue_com_atraso) / NULLIF(COUNT(*), 0),
        2
    ) AS percentual_entregas_atrasadas
FROM entregas
GROUP BY estado
ORDER BY percentual_entregas_atrasadas DESC, pedidos_entregues DESC;
