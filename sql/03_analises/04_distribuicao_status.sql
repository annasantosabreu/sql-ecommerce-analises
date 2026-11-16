-- 04. Distribuicao dos pedidos por status.
-- Todos os pedidos entram nesta visao, inclusive cancelados.
-- Os status sao categorias mutuamente exclusivas no modelo atual.

WITH contagem AS (
    SELECT status, COUNT(*) AS pedidos
    FROM pedidos
    GROUP BY status
)
SELECT
    status,
    pedidos,
    ROUND(100.0 * pedidos / NULLIF(SUM(pedidos) OVER (), 0), 2) AS percentual_pedidos
FROM contagem
ORDER BY pedidos DESC, status;
