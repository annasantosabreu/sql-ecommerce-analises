-- Distribuição de todos os pedidos por status.
SELECT status, COUNT(*) AS quantidade
FROM pedidos
GROUP BY status
ORDER BY quantidade DESC, status;
