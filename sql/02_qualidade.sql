-- Relatorio de verificacoes de qualidade.
-- Contagens de entregas sem aprovacao e pedidos sem avaliacao sao
-- ocorrencias intencionais do conjunto sintetico, nao falhas de carga.

\echo '1) Pedidos sem itens'
SELECT COUNT(*) AS pedidos_sem_itens
FROM pedidos p
LEFT JOIN itens_pedido i ON i.pedido_id = p.id
WHERE i.pedido_id IS NULL;

\echo '2) Pedidos sem pagamento'
SELECT COUNT(*) AS pedidos_sem_pagamento
FROM pedidos p
LEFT JOIN pagamentos pg ON pg.pedido_id = p.id
WHERE pg.pedido_id IS NULL;

\echo '3) Diferencas entre pagamentos e itens + frete (esperado: zero)'
WITH totais_itens AS (
    SELECT pedido_id, SUM(preco + frete) AS total_itens_frete
    FROM itens_pedido
    GROUP BY pedido_id
), totais_pagamentos AS (
    SELECT pedido_id, SUM(valor) AS total_pago
    FROM pagamentos
    GROUP BY pedido_id
)
SELECT COUNT(*) AS pedidos_com_divergencia
FROM totais_itens i
JOIN totais_pagamentos p USING (pedido_id)
WHERE ABS(i.total_itens_frete - p.total_pago) > 0.01;

\echo '4) Avaliacoes vinculadas a pedidos nao entregues (esperado: zero)'
SELECT COUNT(*) AS avaliacoes_de_pedidos_nao_entregues
FROM avaliacoes a
JOIN pedidos p ON p.id = a.pedido_id
WHERE p.status <> 'entregue';

\echo '5) Entregas sem aprovacao (ocorrencia intencional documentada)'
SELECT COUNT(*) AS entregas_sem_aprovacao
FROM pedidos
WHERE status = 'entregue' AND data_aprovacao IS NULL;

\echo '6) Pedidos sem avaliacao (ocorrencia esperada no conjunto)'
SELECT COUNT(*) AS pedidos_sem_avaliacao
FROM pedidos p
LEFT JOIN avaliacoes a ON a.pedido_id = p.id
WHERE a.id IS NULL;

\echo '7) Pedidos com datas fora de ordem (esperado: zero; CHECK tambem protege a tabela)'
SELECT COUNT(*) AS pedidos_com_datas_invalidas
FROM pedidos
WHERE (data_aprovacao IS NOT NULL AND data_aprovacao < data_compra)
   OR (data_envio IS NOT NULL AND data_envio < COALESCE(data_aprovacao, data_compra))
   OR (data_entrega IS NOT NULL AND (data_envio IS NULL OR data_entrega < data_envio))
   OR data_estimada_entrega < data_compra;

\echo '8) Distribuicao de status'
SELECT status, COUNT(*) AS quantidade
FROM pedidos
GROUP BY status
ORDER BY quantidade DESC;
